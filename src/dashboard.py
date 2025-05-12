import streamlit as st
import pandas as pd
import json
import time
import sqlite3
from config import TITLE, LOG_DIR
from components.charts import plot_time_series
from components.alerts import check_alerts
import os
import groq  # For Groq API
import folium
from streamlit_folium import st_folium
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# --- Configuration ---
os.makedirs(LOG_DIR, exist_ok=True)
DB_FILE = f"{LOG_DIR}/genset_data.db"


# --- Groq API Setup ---
load_dotenv()  # Keep this if you still want local .env support
GROQ_API_KEY = os.getenv("GROQ_API_KEY", st.secrets.get("groq", {}).get("api_key", "default-fallback-key"))
client = groq.Groq(api_key=GROQ_API_KEY)
# --- Database Functions ---
def db_connect():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def db_init():
    """Initializes the database and creates the sensor_data table if it doesn't exist."""
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    timestamp TEXT PRIMARY KEY,
                    fuel_level REAL,
                    temperature REAL,
                    pressure REAL,
                    latitude REAL,
                    longitude REAL
                )
            """)
            # Check and add latitude/longitude columns if they don't exist
            cursor.execute("PRAGMA table_info(sensor_data)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'latitude' not in columns:
                cursor.execute("ALTER TABLE sensor_data ADD COLUMN latitude REAL")
            if 'longitude' not in columns:
                cursor.execute("ALTER TABLE sensor_data ADD COLUMN longitude REAL")
            conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")

def db_insert_data(data):
    """Inserts a dictionary of sensor data into the database."""
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO sensor_data (timestamp, fuel_level, temperature, pressure, latitude, longitude)
                VALUES (:timestamp, :fuel_level, :temperature, :pressure, :latitude, :longitude)
            """, data)
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database insert error: {e}")

def db_insert_batch_data(df: pd.DataFrame):
    """Inserts a batch of sensor data from a DataFrame into the database."""
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                data = {
                    "timestamp": row['timestamp'],
                    "fuel_level": row['fuel_level'],
                    "temperature": row['temperature'],
                    "pressure": row['pressure'],
                    "latitude": row.get('latitude', None),
                    "longitude": row.get('longitude', None)
                }
                cursor.execute("""
                    INSERT OR IGNORE INTO sensor_data (timestamp, fuel_level, temperature, pressure, latitude, longitude)
                    VALUES (:timestamp, :fuel_level, :temperature, :pressure, :latitude, :longitude)
                """, data)
            conn.commit()
        st.success(f"Successfully uploaded {len(df)} records to the database.")
    except sqlite3.Error as e:
        st.error(f"Database batch insert error: {e}")

def db_get_data(start_dt=None, end_dt=None):
    """Retrieves data from the database, optionally filtering by date."""
    try:
        with db_connect() as conn:
            query = "SELECT timestamp, fuel_level, temperature, pressure, latitude, longitude FROM sensor_data"
            params = {}
            conditions = []
            if start_dt:
                conditions.append("timestamp >= :start_date")
                params['start_date'] = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
            if end_dt:
                conditions.append("timestamp <= :end_date")
                params['end_date'] = end_dt.strftime("%Y-%m-%d") + " 23:59:59"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY timestamp ASC"
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
    except sqlite3.Error as e:
        st.error(f"Database query error: {e}")
        return pd.DataFrame(columns=['timestamp', 'fuel_level', 'temperature', 'pressure', 'latitude', 'longitude'])

# --- AI Prediction with Groq API ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=32),
    retry=retry_if_exception_type(Exception)
)
def predict_with_groq(data: pd.Series):
    """Uses Groq API to provide tailored responses based on sensor data."""
    fuel_level = data['fuel_level']
    temperature = data['temperature']
    pressure = data['pressure']
    fuel_safe = 20 <= fuel_level <= 100
    temp_safe = temperature < 70
    press_safe = 120 <= pressure <= 180

    # Dynamic prompt based on sensor conditions
    prompt = "You are an AI assistant for a genset monitoring system. Analyze the following sensor data and provide a detailed response:\n"
    prompt += f"- Fuel Level: {fuel_level:.1f}% (Safe range: 20-100%)\n"
    prompt += f"- Temperature: {temperature:.1f}°C (Safe range: <70°C)\n"
    prompt += f"- Pressure: {pressure:.1f} psi (Safe range: 120-180 psi)\n"
    prompt += "Based on the data, provide a status (Safe or Unsafe) and a detailed recommendation. If any parameter is out of range:\n"
    prompt += "- For low fuel (<20%), suggest refueling and monitoring usage.\n"
    prompt += "- For high fuel (>100%), warn of a sensor error and recommend inspection.\n"
    prompt += "- For high temperature (>=70°C), suggest cooling the system and checking for overheating.\n"
    prompt += "- For low pressure (<120 psi), recommend checking the pressure system.\n"
    prompt += "- For high pressure (>180 psi), advise immediate shutdown and inspection.\n"
    prompt += "If all parameters are safe, offer a positive remark."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_response = response.choices[0].message.content.strip()
        # Parse the response to extract status and recommendation
        lines = ai_response.split('\n')
        status = "Safe" if "Safe" in ai_response else "Unsafe"
        recommendation = ai_response.split("Recommendation:")[-1].strip() if "Recommendation:" in ai_response else ai_response
        return status, recommendation
    except Exception as e:
        st.error(f"Error with Groq API: {e}")
        # Fallback: Manual check if API fails
        issues = []
        if not fuel_safe:
            issues.append("Fuel Level" + (" (refuel and monitor)" if fuel_level < 20 else " (sensor error, inspect)"))
        if not temp_safe:
            issues.append("Temperature (cool system, check overheating)")
        if not press_safe:
            issues.append("Pressure" + (" (check pressure system)" if pressure < 120 else " (shutdown, inspect)"))
        status = "Unsafe" if issues else "Safe"
        recommendation = ", ".join(issues) if issues else "All systems are operating normally."
        return status, recommendation

# --- Map Visualization ---
def display_map(df_data, key_prefix="map"):
    """Displays a map with the latest GPS coordinates."""
    if df_data.empty or 'latitude' not in df_data.columns or 'longitude' not in df_data.columns:
        st.info("No GPS data available to display on the map.")
        return

    # Get the latest non-null GPS coordinates
    latest_gps = df_data.dropna(subset=['latitude', 'longitude']).iloc[-1]
    latitude = latest_gps['latitude']
    longitude = latest_gps['longitude']

    # Create a Folium map centered on the latest coordinates
    m = folium.Map(location=[latitude, longitude], zoom_start=15)

    # Add a marker for the latest position
    folium.Marker(
        [latitude, longitude],
        popup=f"Timestamp: {latest_gps['timestamp']}<br>Fuel: {latest_gps['fuel_level']:.1f}%<br>Temp: {latest_gps['temperature']:.1f}°C<br>Pressure: {latest_gps['pressure']:.1f} psi",
        tooltip="Genset Location"
    ).add_to(m)

    # Render the map in Streamlit
    st_folium(m, width=700, height=500, key=f"{key_prefix}_folium")

# --- JSON Data Processing ---
def process_json_sensor_data(json_data):
    """Processes JSON sensor data and inserts it into the database."""
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        if not isinstance(data, list):
            data = [data]  # Ensure it's a list for batch processing
        for item in data:
            formatted_data = {
                "timestamp": item.get("timestamp", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),
                "fuel_level": float(item.get("fuel_level", 0.0)),
                "temperature": float(item.get("temperature", 0.0)),
                "pressure": float(item.get("pressure", 0.0)),
                "latitude": float(item.get("location", {}).get("lat", 0.0)),
                "longitude": float(item.get("location", {}).get("lon", 0.0))
            }
            db_insert_data(formatted_data)
        st.success(f"Processed {len(data)} JSON sensor data record(s).")
    except Exception as e:
        st.error(f"Error processing JSON data: {e}")

# --- Streamlit UI Configuration ---
st.set_page_config(page_title=TITLE, layout="wide")

# --- Initialize Database ---
db_init()

# --- Initialize Session State ---
# Ensure session state variables are initialized at the start
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'genset_status' not in st.session_state:
    st.session_state.genset_status = False
if 'last_timestamp' not in st.session_state:
    st.session_state.last_timestamp = None  # Track the latest timestamp for data updates

# --- Sidebar ---
st.sidebar.title("Settings")
update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 60, 30)  # Default to 30 to avoid API rate limits
default_start = pd.to_datetime("today").date() - pd.Timedelta(days=7)
default_end = pd.to_datetime("today").date()
start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Manual Sensor Data Input
st.sidebar.markdown("### Update Sensor Data Manually")
fuel_level = st.sidebar.number_input("Fuel Level (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
temperature = st.sidebar.number_input("Temperature (°C)", min_value=0.0, max_value=150.0, value=60.0, step=0.1)
pressure = st.sidebar.number_input("Pressure (psi)", min_value=0.0, max_value=300.0, value=150.0, step=0.1)
latitude = st.sidebar.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.01)
longitude = st.sidebar.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.01)

if st.sidebar.button("Update Sensor Data"):
    data = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fuel_level": fuel_level,
        "temperature": temperature,
        "pressure": pressure,
        "latitude": latitude,
        "longitude": longitude
    }
    db_insert_data(data)
    st.sidebar.success(f"Data updated at {data['timestamp']}")

# JSON Sensor Data Input
st.sidebar.markdown("### Update Sensor Data via JSON")
json_input = st.sidebar.text_area("Paste JSON Data", height=150, value='{"timestamp": "2025-05-11 00:56:41", "fuel_level": 58.455481074169185, "temperature": 109.74154493544458, "pressure": 45.7327093894346, "location": {"lat": -15.3875, "lon": 28.3228}}')
if st.sidebar.button("Upload JSON Data"):
    process_json_sensor_data(json_input)

# File Upload for Sensor Data
st.sidebar.markdown("### Upload Sensor Data File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV or JSON file", type=["csv", "json"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_uploaded = pd.read_csv(uploaded_file)
            required_columns = ['timestamp', 'fuel_level', 'temperature', 'pressure']
            optional_columns = ['latitude', 'longitude']
            if not all(col in df_uploaded.columns for col in required_columns):
                st.sidebar.error("CSV must contain columns: timestamp, fuel_level, temperature, pressure")
            else:
                df_uploaded['timestamp'] = pd.to_datetime(df_uploaded['timestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")
                for col in optional_columns:
                    if col not in df_uploaded.columns:
                        df_uploaded[col] = None
                db_insert_batch_data(df_uploaded)
                st.sidebar.success("File data uploaded and stored in the database.")
        elif uploaded_file.name.endswith(".json"):
            json_data = json.load(uploaded_file)
            process_json_sensor_data(json_data)
    except Exception as e:
        st.sidebar.error(f"Error processing uploaded file: {e}")

# --- Title and Genset Status ---
st.title(TITLE)
st.markdown("### Genset Monitoring")

col1, col2 = st.columns([1, 5])
with col1:
    if st.session_state.genset_status:
        if st.button("Turn Genset OFF"):
            st.session_state.genset_status = False
            st.toast("Turning Genset OFF...", icon="🔌")
    else:
        if st.button("Turn Genset ON"):
            st.session_state.genset_status = True
            st.toast("Turning Genset ON...", icon="💡")

with col2:
    status_color = "green" if st.session_state.genset_status else "red"
    st.markdown(f"**Genset Status:** <span style='color:{status_color};'>{'ON' if st.session_state.genset_status else 'OFF'}</span>", unsafe_allow_html=True)

# --- Main Area ---
# Retrieve Data from Database
df_data = db_get_data(start_date, end_date)

# Check if new data has been added
new_data = False
if not df_data.empty:
    latest_timestamp = df_data['timestamp'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S")
    if st.session_state.last_timestamp is None or latest_timestamp > st.session_state.last_timestamp:
        new_data = True
        st.session_state.last_timestamp = latest_timestamp

# Display Current Metrics
metrics_container = st.container()
with metrics_container:
    st.markdown("### Current Readings")
    if not df_data.empty:
        latest_data = df_data.iloc[-1]
        cols = st.columns(3)
        # Remove 'key' parameter
        cols[0].metric(label="Fuel Level (%)", value=latest_data['fuel_level'])
        cols[1].metric(label="Temperature (°C)", value=latest_data['temperature'])
        cols[2].metric(label="Pressure (psi)", value=latest_data['pressure'])
        st.caption(f"Last updated: {latest_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("No data available. Update sensor data in the sidebar or upload a file.")

# Display Charts
charts_container = st.container()
with charts_container:
    st.markdown("### Historical Data")
    if not df_data.empty:
        plot_time_series(df_data, x_col='timestamp', y_cols=['fuel_level', 'temperature', 'pressure'])
    else:
        st.write("No data to display in charts.")

# Check and Display Alerts
alerts_container = st.container()
with alerts_container:
    st.markdown("### Alerts")
    if not df_data.empty:
        check_alerts(latest_data)
    else:
        st.write("No data for alert checking.")

# Display Map
map_container = st.container()
with map_container:
    st.markdown("### Genset Location")
    display_map(df_data, key_prefix="map")

# AI Prediction with Groq
prediction_container = st.container()
with prediction_container:
    st.markdown("---")
    st.markdown("### AI Sensor Health Prediction")
    if not df_data.empty:
        status, recommendation = predict_with_groq(df_data.iloc[-1])  # Use latest row for prediction
        if status == "Safe":
            st.success("✅ " + recommendation)
        else:
            st.error("⚠️ " + recommendation)

        # Display the latest 5 readings in a table
        table_placeholder = st.empty()
        with table_placeholder:
            if new_data or st.session_state.last_timestamp is None:
                st.dataframe(df_data.tail(5).round(2), use_container_width=True, key=f"ai_data_{latest_timestamp}")
            elif st.session_state.last_timestamp is not None:
                # Display the last rendered table if no new data
                st.dataframe(df_data.tail(5).round(2), use_container_width=True, key=f"ai_data_{st.session_state.last_timestamp}")
    else:
        st.write("No data for AI prediction.")

# Auto-refresh mechanism
current_time = time.time()
if current_time - st.session_state.last_update >= update_interval:
    st.session_state.last_update = current_time
    st.rerun()  # Updated from st.experimental_rerun()
import streamlit as st
import pandas as pd
import json
import time
import sqlite3 # Import sqlite3
from config import TITLE, LOG_DIR
from components.charts import plot_time_series # Assuming this exists and takes a DataFrame
from components.alerts import check_alerts     # Assuming this exists

# Dummy data generation
import random
from datetime import datetime, date # Import date for sidebar
import os

# --- Configuration ---
# Ensure LOG_DIR exists
os.makedirs(LOG_DIR, exist_ok=True)

DB_FILE = f"{LOG_DIR}/genset_data.db" # Database file path

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
                    pressure REAL
                )
            """)
            conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")
        print(f"Database initialization error: {e}") # Also print to console

def db_insert_data(data):
    """Inserts a dictionary of sensor data into the database."""
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            # Use INSERT OR IGNORE to avoid errors if a timestamp somehow repeats
            cursor.execute("""
                INSERT OR IGNORE INTO sensor_data (timestamp, fuel_level, temperature, pressure)
                VALUES (:timestamp, :fuel_level, :temperature, :pressure)
            """, data)
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database insert error: {e}")
        print(f"Database insert error: {e}") # Also print to console


def db_get_data(start_dt=None, end_dt=None):
    """Retrieves data from the database, optionally filtering by date."""
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            query = "SELECT timestamp, fuel_level, temperature, pressure FROM sensor_data"
            params = {}
            conditions = []

            # --- Date Filtering (Basic Implementation) ---
            # Convert date objects to string format compatible with TEXT storage
            if start_dt:
                conditions.append("timestamp >= :start_date")
                # Append time to make it comparable if timestamps include time
                params['start_date'] = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
            if end_dt:
                conditions.append("timestamp <= :end_date")
                 # Append time to make it comparable
                params['end_date'] = end_dt.strftime("%Y-%m-%d") + " 23:59:59"

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp ASC" # Ensure chronological order for plotting

            df = pd.read_sql_query(query, conn, params=params)
            # Convert timestamp column to datetime objects after fetching
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
    except sqlite3.Error as e:
        st.error(f"Database query error: {e}")
        print(f"Database query error: {e}") # Also print to console
        # Return empty DataFrame on error to avoid breaking downstream code
        return pd.DataFrame(columns=['timestamp', 'fuel_level', 'temperature', 'pressure'])
    except Exception as e:
        st.error(f"Error processing database data: {e}")
        print(f"Error processing database data: {e}")
        return pd.DataFrame(columns=['timestamp', 'fuel_level', 'temperature', 'pressure'])


def generate_dummy_data():
    """Generates a single dummy data record."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fuel_level": random.uniform(10.0, 90.0), # Use float for realism
        "temperature": random.uniform(20.0, 80.0),
        "pressure": random.uniform(100.0, 200.0),
    }

# --- Initialize Database ---
db_init()

# --- Streamlit UI Configuration ---
st.set_page_config(page_title=TITLE, layout="wide")

# --- Sidebar ---
st.sidebar.title("Settings")
update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 10, 5)
# Use datetime.now().date() for default values
default_start = date.today() - pd.Timedelta(days=7) # Default to last 7 days
default_end = date.today()
start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Add a button to manually trigger data generation (useful for testing)
if st.sidebar.button("Generate Dummy Data Point"):
    dummy_data = generate_dummy_data()
    db_insert_data(dummy_data)
    st.sidebar.success(f"Added: {dummy_data['timestamp']}")

# --- Title and Genset Status ---
st.title(TITLE)
st.markdown("### Genset Monitoring")

if 'genset_status' not in st.session_state:
    st.session_state.genset_status = False # Default to OFF

# Button logic
col1, col2 = st.columns([1, 5]) # Allocate space for button and status text
with col1:
    if st.session_state.genset_status:
        if st.button("Turn Genset OFF"):
            st.session_state.genset_status = False
            # Add code here to send the "OFF" command to your genset
            st.toast("Turning Genset OFF...", icon="🔌") # Use toast for less intrusive feedback
    else:
        if st.button("Turn Genset ON"):
            st.session_state.genset_status = True
            # Add code here to send the "ON" command to your genset
            st.toast("Turning Genset ON...", icon="💡")

with col2:
    status_color = "green" if st.session_state.genset_status else "red"
    st.markdown(f"**Genset Status:** <span style='color:{status_color};'>{'ON' if st.session_state.genset_status else 'OFF'}</span>", unsafe_allow_html=True)


# --- Main Area Placeholders ---
metrics_placeholder = st.empty()
charts_placeholder = st.empty()
alerts_placeholder = st.empty()
prediction_placeholder = st.container() # Use a container for the AI section

# --- Main loop for data updates and display ---
while True:
    try:
        # --- Generate and Store Data (Simulated) ---
        # In a real scenario, you might read from a sensor/API here instead of generating
        # For this example, we only generate data when the button is pressed,
        # or you could uncomment the next lines to generate data automatically in the loop
        # current_data = generate_dummy_data()
        # db_insert_data(current_data)

        # --- Retrieve Data from Database ---
        # Pass the selected dates from the sidebar to the query function
        df_data = db_get_data(start_date, end_date)

        # --- Display Current Metrics ---
        if not df_data.empty:
            latest_data = df_data.iloc[-1] # Get the last row for current status

            with metrics_placeholder.container():
                st.markdown("### Current Readings")
                cols = st.columns(3)
                cols[0].metric("Fuel Level (%)", f"{latest_data['fuel_level']:.1f}")
                cols[1].metric("Temperature (°C)", f"{latest_data['temperature']:.1f}")
                cols[2].metric("Pressure (psi)", f"{latest_data['pressure']:.1f}")
                st.caption(f"Last updated: {latest_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            metrics_placeholder.info("No data available for the selected period. Generate some data or adjust dates.")

        # --- Display Charts ---
        with charts_placeholder.container():
            st.markdown("### Historical Data")
            if not df_data.empty:
                 # Check if your plot_time_series can handle multiple columns
                 # Assuming plot_time_series takes df, x_col, y_cols list
                 plot_time_series(df_data, x_col='timestamp', y_cols=['fuel_level', 'temperature', 'pressure'])
                 # If plot_time_series plots only one metric, call it multiple times:
                 # st.line_chart(df_data.set_index('timestamp')[['fuel_level', 'temperature', 'pressure']]) # Simple alternative
            else:
                 st.write("No data to display in charts.")


        # --- Check and Display Alerts ---
        with alerts_placeholder.container():
             st.markdown("### Alerts")
             if not df_data.empty:
                 # Assuming check_alerts takes the latest data point (as a Series or dict)
                 check_alerts(latest_data)
             else:
                 st.write("No data for alert checking.")

        # --- AI Fuel Level Prediction Placeholder ---
        with prediction_placeholder:
            st.markdown("---") # Separator
            st.markdown("### AI Fuel Level Prediction")
            if not df_data.empty:
                # TODO: Implement AI Prediction Logic Here
                # 1. Load your trained AI/ML model (e.g., using pickle, joblib, tensorflow, pytorch)
                #    model = load_model('path/to/your/fuel_predictor.pkl')
                # 2. Preprocess the historical data (df_data) as required by your model
                #    (e.g., feature engineering, scaling, creating sequences)
                #    features = preprocess_data(df_data)
                # 3. Make a prediction for a future time step
                #    predicted_fuel = model.predict(features) # Predict next N hours/days
                # 4. Display the prediction
                #    st.metric("Predicted Fuel Level (next 24h)", f"{predicted_fuel[0]:.1f}%") # Example
                st.info("AI prediction model integration pending.")
                st.write("Historical data available for prediction (first 5 rows):")
                st.dataframe(df_data.tail().round(2)) # Show tail for recent data
            else:
                st.write("Insufficient data for AI prediction.")


        # --- Wait for the next update cycle ---
        time.sleep(update_interval)

        # --- Rerun Streamlit ---
        # Streamlit reruns the script automatically when state changes (like button clicks)
        # or periodically if using techniques like st.rerun() within the loop,
        # but for this structure, the `while True` with `time.sleep` and updating
        # placeholders works well for periodic background-like updates.
        # However, button clicks will trigger a full rerun anyway.
        # For cleaner state management with loops, consider Session State more heavily.

    except KeyboardInterrupt:
        print("Stopping the application.")
        break
    except Exception as e:
        st.error(f"An unexpected error occurred in the main loop: {e}")
        print(f"An unexpected error occurred in the main loop: {e}")
        time.sleep(update_interval) # Wait before retrying after an error
import streamlit as st
import pandas as pd
import json
import time
import requests
from config import TITLE, LOG_DIR
from components.charts import plot_time_series
from components.alerts import check_alerts
import os
import groq  # For Groq API
from dotenv import load_dotenv

from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
os.makedirs(LOG_DIR, exist_ok=True)

# --- Initialize session state safely ---
def initialize_session_state():
    """Initialize all session state variables safely"""
    if "api_url" not in st.session_state:
        st.session_state["api_url"] = "https://genset-monitoring.onrender.com"
    if "esp32_relay_state" not in st.session_state:
        st.session_state["esp32_relay_state"] = False
    if "last_predicted_timestamp" not in st.session_state:
        st.session_state["last_predicted_timestamp"] = None
    if "last_groq_result" not in st.session_state:
        st.session_state["last_groq_result"] = ("Unknown", "No prediction yet.")
    if "groq_client_initialized" not in st.session_state:
        st.session_state["groq_client_initialized"] = False
    if "groq_error_count" not in st.session_state:
        st.session_state["groq_error_count"] = 0

# Initialize session state
initialize_session_state()

# --- Groq API Setup with error handling ---
def setup_groq_client():
    """Setup Groq client with proper error handling"""
    try:
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
        if not GROQ_API_KEY or GROQ_API_KEY == "default-fallback-key":
            st.warning("⚠️ GROQ_API_KEY not found. AI analysis will be disabled.")
            return None
        
        client = groq.Groq(api_key=GROQ_API_KEY)
        st.session_state["groq_client_initialized"] = True
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq client: {e}")
        st.session_state["groq_client_initialized"] = False
        return None

# Initialize Groq client
groq_client = setup_groq_client()

# --- API Server URL ---
API_SERVER_URL = st.sidebar.text_input(
    "API Server URL",
    value=st.session_state.get("api_url", "https://genset-monitoring.onrender.com"),
    help="Enter the base URL of your API server (e.g., https://genset-monitoring.onrender.com or http://localhost:8000)"
)
st.session_state["api_url"] = API_SERVER_URL

# Sidebar controls for relay and buzzer
st.sidebar.title("Genset Monitoring Controls")
relay_state = st.sidebar.radio("Relay State", ("ON", "OFF"), index=0 if st.session_state.get('esp32_relay_state', False) else 1)
relay_notification_placeholder = st.sidebar.empty()
buzzer_notification_placeholder = st.sidebar.empty()
if st.sidebar.button("Set Relay State"):
    relay_notification_placeholder.empty()  # Clear previous notification
    try:
        resp = requests.post(f"{API_SERVER_URL}/api/relay", json={"state": relay_state.lower()})
        if resp.status_code == 200:
            relay_notification_placeholder.success(f"Relay turned {relay_state}")
            st.session_state["esp32_relay_state"] = (relay_state == "ON")
        else:
            relay_notification_placeholder.error("Failed to set relay state")
    except Exception as e:
        relay_notification_placeholder.error(f"Relay control error: {e}")

if st.sidebar.button("Trigger Buzzer"):
    buzzer_notification_placeholder.empty()  # Clear previous notification
    try:
        resp = requests.post(f"{API_SERVER_URL}/api/buzzer")
        if resp.status_code == 200:
            buzzer_notification_placeholder.success("Buzzer triggered!")
        else:
            buzzer_notification_placeholder.error("Failed to trigger buzzer")
    except Exception as e:
        buzzer_notification_placeholder.error(f"Buzzer control error: {e}")

# --- Fetch latest and historical data from API ---
def fetch_latest_data_from_api(api_url):
    try:
        resp = requests.get(f"{api_url}/api/sensor-data", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"API returned status code: {resp.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching data from API: {e}")
        return None

def fetch_historical_data_from_api(api_url, limit=100):
    try:
        resp = requests.get(f"{api_url}/api/sensor-data/all?limit={limit}", timeout=5)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            return pd.DataFrame(data)
        else:
            st.error(f"API returned status code: {resp.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching historical data from API: {e}")
        return pd.DataFrame()

# --- Fetch relay status from API ---
def fetch_relay_status_from_api(api_url):
    try:
        resp = requests.get(f"{api_url}/api/commands", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('relay', 'off').upper()
        else:
            st.error(f"API returned status code: {resp.status_code} for relay status")
            return 'OFF'
    except Exception as e:
        st.error(f"Error fetching relay status from API: {e}")
        return 'OFF'

# --- Main Area: Genset Status and Metrics ---
st.title(TITLE)
st.markdown("### Genset Monitoring Dashboard")
st.caption("🔄 Dashboard auto-refreshes every 3 seconds for live data.")

latest_data = fetch_latest_data_from_api(API_SERVER_URL)
historical_df = fetch_historical_data_from_api(API_SERVER_URL, limit=100)
relay_status_api = fetch_relay_status_from_api(API_SERVER_URL)

# Ensure timestamp is parsed and sorted ascending for charts and tables
if not historical_df.empty and 'timestamp' in historical_df.columns:
    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])
    historical_df = historical_df.sort_values('timestamp', ascending=True)

if latest_data and isinstance(latest_data, dict) and 'temperature' in latest_data:
    st.success(f"Last Updated: {latest_data.get('timestamp', '')}")
else:
    st.warning("No sensor data available from API.")

# --- Display relay and buzzer status ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Relay Status", relay_status_api)
with col2:
    st.info("Buzzer status available on trigger")

# --- Display Current Metrics ---
st.markdown("### 📊 Current Sensor Readings")
if latest_data:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="⛽ Fuel Level", 
            value=f"{latest_data.get('fuel_level', 0.0):.1f}%",
            delta=None,
            help="Current fuel level percentage"
        )
    with col2:
        st.metric(
            label="🌡️ Temperature", 
            value=f"{latest_data.get('temperature', 0.0):.1f}°C",
            delta=None,
            help="Current temperature in Celsius"
        )
    st.markdown("---")
    st.info(f"🕒 **Last Updated:** {latest_data.get('timestamp', '')}")
else:
    st.warning("No sensor data available from API.")

# Display Charts
charts_container = st.container()
with charts_container:
    st.markdown("### 📈 Historical Data")
    if not historical_df.empty:
        plot_time_series(historical_df, x_col='timestamp', y_cols=['fuel_level', 'temperature'])
    else:
        st.write("No data to display in charts.")

# Real-time Data Table
st.markdown("### 📋 Real-time Data Table")
if not historical_df.empty:
    # Show the latest 10 readings, most recent at the top
    latest_readings = historical_df.sort_values('timestamp', ascending=False).head(10).iloc[::-1].copy()
    display_data = latest_readings[['timestamp', 'fuel_level', 'temperature']].copy()
    display_data['timestamp'] = pd.to_datetime(display_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    display_data['fuel_level'] = display_data['fuel_level'].round(1).astype(str) + '%'
    display_data['temperature'] = display_data['temperature'].round(1).astype(str) + '°C'
    display_data.columns = ['Timestamp', 'Fuel Level', 'Temperature']
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": st.column_config.TextColumn("🕒 Timestamp", width="medium"),
            "Fuel Level": st.column_config.TextColumn("⛽ Fuel Level", width="small"),
            "Temperature": st.column_config.TextColumn("🌡️ Temperature", width="small")
        }
    )
    # Add summary statistics
    st.markdown("#### 📊 Summary Statistics")
    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.metric("Average Fuel Level", f"{historical_df['fuel_level'].mean():.1f}%")
        st.metric("Min Fuel Level", f"{historical_df['fuel_level'].min():.1f}%")
        st.metric("Max Fuel Level", f"{historical_df['fuel_level'].max():.1f}%")
    with summary_col2:
        st.metric("Average Temperature", f"{historical_df['temperature'].mean():.1f}°C")
        st.metric("Min Temperature", f"{historical_df['temperature'].min():.1f}°C")
        st.metric("Max Temperature", f"{historical_df['temperature'].max():.1f}°C")
else:
    st.info("No data available for the data table.")

# Check and Display Alerts
alerts_container = st.container()
with alerts_container:
    st.markdown("### Alerts")
    if latest_data:
        check_alerts(latest_data)
    else:
        st.write("No data for alert checking.")

# AI Prediction with Groq - Optimized for token efficiency
def predict_with_groq(data: dict, df_history: pd.DataFrame = None):
    """Optimized Groq prediction with shorter prompts and error handling"""
    if not groq_client or not st.session_state.get("groq_client_initialized", False):
        return "Unknown", "AI analysis unavailable - Groq client not initialized"
    
    # Check error count to prevent excessive API calls
    if st.session_state.get("groq_error_count", 0) > 3:
        return "Unknown", "AI analysis temporarily disabled due to errors"
    
    fuel_level = data.get('fuel_level', 0)
    temperature = data.get('temperature', 0)
    
    # Create shorter, more focused prompt to save tokens
    prompt = f"Genset status: Fuel {fuel_level:.1f}% (safe: 20-100%), Temp {temperature:.1f}°C (safe: <70°C). Status and brief recommendation:"
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,  # Limit response length to save tokens
            temperature=0.3  # Lower temperature for more consistent responses
        )
        ai_response = response.choices[0].message.content.strip()
        
        # Reset error count on success
        st.session_state["groq_error_count"] = 0
        
        # Simple status detection
        status = "Safe" if any(word in ai_response.lower() for word in ["safe", "normal", "ok", "good"]) else "Unsafe"
        return status, ai_response
        
    except Exception as e:
        # Increment error count
        st.session_state["groq_error_count"] = st.session_state.get("groq_error_count", 0) + 1
        st.error(f"Error with Groq API: {e}")
        return "Unknown", "AI analysis unavailable"

prediction_container = st.container()
with prediction_container:
    st.markdown("---")
    st.markdown("### AI Sensor Health Prediction")
    
    # Show Groq status in sidebar
    if not groq_client or not st.session_state.get("groq_client_initialized", False):
        st.sidebar.warning("⚠️ AI Analysis: Disabled (No API Key)")
    elif st.session_state.get("groq_error_count", 0) > 3:
        st.sidebar.error("⚠️ AI Analysis: Temporarily Disabled")
    else:
        st.sidebar.success("✅ AI Analysis: Active")
    
    if latest_data:
        # Only make new predictions if data has changed and Groq is available
        current_timestamp = latest_data.get("timestamp")
        if (current_timestamp != st.session_state.get("last_predicted_timestamp") and 
            groq_client and st.session_state.get("groq_client_initialized", False) and
            st.session_state.get("groq_error_count", 0) <= 3):
            
            with st.spinner("🤖 Analyzing sensor data..."):
                status, recommendation = predict_with_groq(latest_data, historical_df)
                st.session_state["last_predicted_timestamp"] = current_timestamp
                st.session_state["last_groq_result"] = (status, recommendation)
        else:
            status, recommendation = st.session_state.get("last_groq_result", ("Unknown", "No prediction available"))
        
        # Display the result
        if status == "Safe":
            st.success("✅ " + recommendation)
        elif status == "Unsafe":
            st.error("⚠️ " + recommendation)
        else:
            st.info("ℹ️ " + recommendation)
    else:
        st.info("ℹ️ No sensor data available for AI analysis")

# Add this line to auto-refresh every 3 seconds (3000 ms)
st_autorefresh(interval=3000, key="datarefresh")
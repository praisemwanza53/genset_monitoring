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

# --- Groq API Setup ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "default-fallback-key")
client = groq.Groq(api_key=GROQ_API_KEY)

# --- API Server URL ---
if "api_url" not in st.session_state:
    st.session_state["api_url"] = "https://genset-monitoring.onrender.com"
API_SERVER_URL = st.sidebar.text_input(
    "API Server URL",
    value=st.session_state["api_url"],
    help="Enter the base URL of your API server (e.g., https://genset-monitoring.onrender.com or http://localhost:8000)"
)
st.session_state["api_url"] = API_SERVER_URL

# Sidebar controls for relay and buzzer
st.sidebar.title("Genset Monitoring Controls")
relay_state = st.sidebar.radio("Relay State", ("ON", "OFF"), index=0 if st.session_state.get('esp32_relay_state', False) else 1)
if st.sidebar.button("Set Relay State"):
    try:
        resp = requests.post(f"{API_SERVER_URL}/api/relay", json={"state": relay_state.lower()})
        if resp.status_code == 200:
            st.sidebar.success(f"Relay turned {relay_state}")
            st.session_state.esp32_relay_state = (relay_state == "ON")
        else:
            st.sidebar.error("Failed to set relay state")
    except Exception as e:
        st.sidebar.error(f"Relay control error: {e}")

if st.sidebar.button("Trigger Buzzer"):
    try:
        resp = requests.post(f"{API_SERVER_URL}/api/buzzer")
        if resp.status_code == 200:
            st.sidebar.success("Buzzer triggered!")
        else:
            st.sidebar.error("Failed to trigger buzzer")
    except Exception as e:
        st.sidebar.error(f"Buzzer control error: {e}")

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

# --- Main Area: Genset Status and Metrics ---
st.title(TITLE)
st.markdown("### Genset Monitoring Dashboard")
st.caption("🔄 Dashboard auto-refreshes every 3 seconds for live data.")

latest_data = fetch_latest_data_from_api(API_SERVER_URL)
historical_df = fetch_historical_data_from_api(API_SERVER_URL, limit=100)

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
    relay_status = "ON" if st.session_state.get('esp32_relay_state', False) else "OFF"
    st.metric("Relay Status", relay_status)
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

# AI Prediction with Groq
def predict_with_groq(data: dict, df_history: pd.DataFrame = None):
    fuel_level = data['fuel_level']
    temperature = data['temperature']
    prompt = "You are an AI assistant for a genset monitoring system. Analyze the following sensor data and provide a detailed response:\n"
    prompt += f"- Fuel Level: {fuel_level:.1f}% (Safe range: 20-100%)\n"
    prompt += f"- Temperature: {temperature:.1f}°C (Safe range: <70°C)\n"
    if df_history is not None and len(df_history) > 1:
        prompt += "\nHistorical data is available.\n"
    prompt += "\nBased on the data, provide a comprehensive status (Safe or Unsafe) and detailed recommendations.\n"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_response = response.choices[0].message.content.strip()
        status = "Safe" if "Safe" in ai_response else "Unsafe"
        recommendation = ai_response
        return status, recommendation
    except Exception as e:
        st.error(f"Error with Groq API: {e}")
        return "Unknown", "AI analysis unavailable."

prediction_container = st.container()
with prediction_container:
    st.markdown("---")
    st.markdown("### AI Sensor Health Prediction")
    if latest_data:
        status, recommendation = predict_with_groq(latest_data, historical_df)
        if status == "Safe":
            st.success("✅ " + recommendation)
        else:
            st.error("⚠️ " + recommendation)

# Add this line to auto-refresh every 3 seconds (3000 ms)
st_autorefresh(interval=3000, key="datarefresh")
import streamlit as st
import pandas as pd
import json
import time
from config import TITLE, LOG_DIR
from components.charts import plot_time_series
from components.alerts import check_alerts

SENSOR_DATA_FILE = f"{LOG_DIR}/sensor_data.json"

# Streamlit UI Configuration
st.set_page_config(page_title=TITLE, layout="wide")

# Sidebar Configuration
st.sidebar.title("Settings")
update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 10, 5)

# Date Selection Filters
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Dashboard Title
st.title(TITLE)
st.markdown("### Genset Monitoring ")

# Initialize empty lists for time-series data
data_log = {"timestamp": [], "fuel_level": [], "temperature": [], "pressure": []}

# Real-time Data Display
placeholder = st.empty()

while True:
    try:
        with open(SENSOR_DATA_FILE, "r") as f:
            sensor_data = json.load(f)

        # Append data for visualization
        data_log["timestamp"].append(sensor_data["timestamp"])
        data_log["fuel_level"].append(sensor_data["fuel_level"])
        data_log["temperature"].append(sensor_data["temperature"])
        data_log["pressure"].append(sensor_data["pressure"])

        df = pd.DataFrame(data_log)

        with placeholder.container():
            st.write(f"#### Last Updated: {sensor_data['timestamp']}")
            
            # Metrics in a row
            col1, col2, col3 = st.columns(3)
            col1.metric("Fuel Level (%)", sensor_data["fuel_level"], " 🔵")
            col2.metric("Temperature (°C)", sensor_data["temperature"], " 🔴")
            col3.metric("Pressure (kPa)", sensor_data["pressure"], " 🟢")
            
            # Generate Alerts
            check_alerts(sensor_data)
            
            # Charts Layout
            st.markdown("### Sensor Data Trends")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Fuel Level Trend")
                plot_time_series(df[["timestamp", "fuel_level"]].rename(columns={"fuel_level": "value"}), "Fuel Level", "%", "blue")
                
                st.subheader("Pressure Trend")
                plot_time_series(df[["timestamp", "pressure"]].rename(columns={"pressure": "value"}), "Pressure", "kPa", "green")
            
            with col2:
                st.subheader("Temperature Trend")
                plot_time_series(df[["timestamp", "temperature"]].rename(columns={"temperature": "value"}), "Temperature", "°C", "red")
                
        time.sleep(update_interval)
    except Exception as e:
        st.error(f"Error: {e}")

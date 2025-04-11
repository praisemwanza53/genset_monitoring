import streamlit as st
import pandas as pd
import json
import time
from config import TITLE, LOG_DIR
from components.charts import plot_time_series
from components.alerts import check_alerts

# Dummy data generation and file handling
import random
from datetime import datetime
import os

SENSOR_DATA_FILE = f"{LOG_DIR}/sensor_data.json"

def generate_dummy_data():
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fuel_level": random.randint(10, 90),
        "temperature": random.randint(20, 80),
        "pressure": random.randint(100, 200),
    }

if not os.path.exists(SENSOR_DATA_FILE):
    with open(SENSOR_DATA_FILE, "w") as f:
        json.dump(generate_dummy_data(), f)


# Streamlit UI Configuration
st.set_page_config(page_title=TITLE, layout="wide")

# Sidebar
st.sidebar.title("Settings")
update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 10, 5)
start_date = st.sidebar.date_input("Start Date")  # Not used yet
end_date = st.sidebar.date_input("End Date")      # Not used yet

# Title and Genset Status
st.title(TITLE)
st.markdown("### Genset Monitoring")

if 'genset_status' not in st.session_state:
    st.session_state.genset_status = False

# Button logic *outside* the loop!
if st.session_state.genset_status:
    if st.button("Turn Genset OFF"):
        st.session_state.genset_status = False
        # Add code here to send the "OFF" command to your genset
        st.info("Turning Genset OFF...")  # Placeholder for feedback
else:
    if st.button("Turn Genset ON"):
        st.session_state.genset_status = True
        # Add code here to send the "ON" command to your genset
        st.info("Turning Genset ON...")   # Placeholder for feedback

st.write(f"Genset Status: {'ON' if st.session_state.genset_status else 'OFF'}")

# Data and Placeholder
data_log = {"timestamp": [], "fuel_level": [], "temperature": [], "pressure": []}
placeholder = st.empty()


# Main loop for data updates
while True:
    try:
        try:
            with open(SENSOR_DATA_FILE, "r") as f:
                sensor_data = json.load(f)
        except FileNotFoundError:
            sensor_data = generate_dummy_data()
            with open(SENSOR_DATA_FILE, "w") as f: # Write the dummy data so next time u read from file
                json.dump(sensor_data, f, indent=4) 


        # ... (The rest of the data handling, metrics, charts, and alerts code remains the same)


        time.sleep(update_interval)

    except Exception as e:
        st.error(f"Error: {e}")
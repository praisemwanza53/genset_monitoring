# src/components/alerts.py

import streamlit as st
from config import THRESHOLDS

def check_alerts(sensor_data):
    """Check for any anomalies and display alerts."""
    alerts = []
    
    if sensor_data["fuel_level"] < THRESHOLDS["fuel_level"]:
        alerts.append(f"⚠️ Low Fuel Alert: {sensor_data['fuel_level']}% remaining!")

    if sensor_data["temperature"] > THRESHOLDS["temperature"]:
        alerts.append(f"🔥 High Temperature Alert: {sensor_data['temperature']}°C!")

    if sensor_data["pressure"] < THRESHOLDS["pressure"]:
        alerts.append(f"🛠️ Low Pressure Alert: {sensor_data['pressure']} kPa!")

    for alert in alerts:
        st.warning(alert)

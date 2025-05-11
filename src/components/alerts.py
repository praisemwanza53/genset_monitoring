

# components/alerts.py
import streamlit as st
import pandas as pd

# Define thresholds (example)
FUEL_LOW_THRESHOLD = 20
TEMP_HIGH_THRESHOLD = 70
PRESSURE_HIGH_THRESHOLD = 180
PRESSURE_LOW_THRESHOLD = 120

def check_alerts(latest_data: pd.Series):
    """Checks the latest data point for alert conditions."""
    alerts = []
    if latest_data['fuel_level'] < FUEL_LOW_THRESHOLD:
        alerts.append(f"🔴 **Low Fuel Alert:** Level is {latest_data['fuel_level']:.1f}% (Threshold: < {FUEL_LOW_THRESHOLD}%)")
    if latest_data['temperature'] > TEMP_HIGH_THRESHOLD:
        alerts.append(f"🟠 **High Temperature Alert:** Temp is {latest_data['temperature']:.1f}°C (Threshold: > {TEMP_HIGH_THRESHOLD}°C)")
    if latest_data['pressure'] > PRESSURE_HIGH_THRESHOLD:
         alerts.append(f"🟡 **High Pressure Alert:** Pressure is {latest_data['pressure']:.1f} psi (Threshold: > {PRESSURE_HIGH_THRESHOLD} psi)")
    elif latest_data['pressure'] < PRESSURE_LOW_THRESHOLD:
         alerts.append(f"🔵 **Low Pressure Alert:** Pressure is {latest_data['pressure']:.1f} psi (Threshold: < {PRESSURE_LOW_THRESHOLD} psi)")


    if alerts:
        for alert in alerts:
            st.warning(alert) # Display alerts using st.warning or st.error
    else:
        st.success("✅ All systems nominal.")
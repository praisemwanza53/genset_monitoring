

# components/alerts.py
import streamlit as st
import pandas as pd

# Define thresholds (example)
FUEL_LOW_THRESHOLD = 20
TEMP_HIGH_THRESHOLD = 70

def check_alerts(latest_data: pd.Series):
    """Checks the latest data point for alert conditions."""
    alerts = []
    if latest_data['fuel_level'] < FUEL_LOW_THRESHOLD:
        alerts.append(f"\U0001F534 **Low Fuel Alert:** Level is {latest_data['fuel_level']:.1f}% (Threshold: < {FUEL_LOW_THRESHOLD}%)")
    if latest_data['temperature'] > TEMP_HIGH_THRESHOLD:
        alerts.append(f"\U0001F7E0 **High Temperature Alert:** Temp is {latest_data['temperature']:.1f}\u00b0C (Threshold: > {TEMP_HIGH_THRESHOLD}\u00b0C)")

    if alerts:
        for alert in alerts:
            st.warning(alert) # Display alerts using st.warning or st.error
    else:
        st.success("\u2705 All systems nominal.")
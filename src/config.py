# src/config.py

import os

# Dashboard settings
TITLE = "IoT-Based Genset Monitoring System"
THEME = "dark"

# Simulated Data Settings
SIMULATION_INTERVAL = 5  # seconds

# Thresholds for alerts
THRESHOLDS = {
    "fuel_level": 30,    # Trigger alert if fuel < 30%
    "temperature": 90,   # Trigger alert if temp > 90°C
    "pressure": 50       # Trigger alert if pressure < 50 kPa
}

# Logging Directory
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
 

# src/config.py

import os

# Dashboard settings
TITLE = "IoT Genset Monitor"
THEME = "dark"
LOG_DIR = "logs" # Or any directory you prefer
  
# Simulated Data Settings
SIMULATION_INTERVAL = 5  # seconds

# Thresholds for alerts
THRESHOLDS = {
    "fuel_level": 30,    # Trigger alert if fuel < 30%
    "temperature": 90   # Trigger alert if temp > 90°C
}

# Logging Directory
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
 

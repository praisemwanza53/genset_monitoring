# src/simulate.py

import pandas as pd
import numpy as np
import time
import json
import os
from config import SIMULATION_INTERVAL, LOG_DIR

OUTPUT_FILE = os.path.join(LOG_DIR, "sensor_data.json")

def generate_fake_data():
    """Generates random sensor readings for the genset."""
    return {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fuel_level": np.random.uniform(10, 100),   # 10% - 100%
        "temperature": np.random.uniform(50, 110),  # 50°C - 110°C
        "pressure": np.random.uniform(30, 100),     # 30 - 100 kPa
        "location": {"lat": -15.3875, "lon": 28.3228}  # Simulated GPS coordinates
    }

def run_simulation():
    """Continuously generates and writes sensor data to a JSON file."""
    while True:
        data = generate_fake_data()
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Updated sensor data: {data}")
        time.sleep(SIMULATION_INTERVAL)

if __name__ == "__main__":
    run_simulation()
 

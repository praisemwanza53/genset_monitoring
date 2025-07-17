import sqlite3
import os
from datetime import datetime

# Force DB_FILE to use the correct path for both API and dashboard
DB_FILE = os.path.join(os.getcwd(), "data", "genset_monitoring.db")

def init_database():
    """Initializes the database and creates the sensor_data table if it doesn't exist."""
    db_dir = os.path.dirname(DB_FILE)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                timestamp TEXT PRIMARY KEY,
                fuel_level REAL,
                temperature REAL
            )
        ''')
        conn.commit()

def insert_sensor_data(temperature, fuel_level, timestamp):
    """Inserts a new sensor data record into the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO sensor_data (
                timestamp, fuel_level, temperature
            ) VALUES (?, ?, ?)
        ''', (timestamp.strftime("%Y-%m-%d %H:%M:%S"), fuel_level, temperature))
        conn.commit()

def get_latest_data():
    """Gets the latest sensor data from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, fuel_level, temperature
            FROM sensor_data ORDER BY timestamp DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        if row:
            return {
                "timestamp": row[0],
                "fuel_level": row[1],
                "temperature": row[2],
            }
        return None 
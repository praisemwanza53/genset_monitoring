import sqlite3
from config import LOG_DIR

DB_FILE = f"{LOG_DIR}/genset_data.db"

def db_connect():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

try:
    with db_connect() as conn:
        cursor = conn.cursor()
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in the database:", tables)

        # Check the structure of the sensor_data table
        cursor.execute("PRAGMA table_info(sensor_data)")
        columns = cursor.fetchall()
        print("Columns in sensor_data table:")
        for column in columns:
            print(column)

        # Optionally, view some data
        cursor.execute("SELECT * FROM sensor_data LIMIT 5")
        data = cursor.fetchall()
        print("Sample data from sensor_data:", data)
except sqlite3.Error as e:
    print(f"Error: {e}")
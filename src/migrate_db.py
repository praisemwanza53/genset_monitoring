import sqlite3
from config import LOG_DIR  # Import LOG_DIR from your config

# Define the database file path
DB_FILE = f"{LOG_DIR}/genset_data.db"

def db_connect():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

# Migration script
try:
    with db_connect() as conn:
        cursor = conn.cursor()
        # Check if columns exist before adding them
        cursor.execute("PRAGMA table_info(sensor_data)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'latitude' not in columns:
            cursor.execute("ALTER TABLE sensor_data ADD COLUMN latitude REAL")
            print("Added latitude column.")
        else:
            print("Latitude column already exists.")
        if 'longitude' not in columns:
            cursor.execute("ALTER TABLE sensor_data ADD COLUMN longitude REAL")
            print("Added longitude column.")
        else:
            print("Longitude column already exists.")
        conn.commit()
    print("Database migration completed successfully.")
except sqlite3.Error as e:
    print(f"Error during database migration: {e}")
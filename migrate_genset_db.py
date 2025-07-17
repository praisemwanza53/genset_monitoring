import sqlite3
import os

DB_PATH = os.path.join("data", "genset_monitoring.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Create a new table with the correct schema
c.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data_new (
        timestamp TEXT PRIMARY KEY,
        fuel_level REAL,
        temperature REAL
    )
''')

# 2. Copy relevant data from the old table
c.execute('''
    INSERT OR IGNORE INTO sensor_data_new (timestamp, fuel_level, temperature)
    SELECT timestamp, fuel_level, temperature FROM sensor_data
''')

conn.commit()

# 3. Drop the old table and rename the new one
c.execute('DROP TABLE sensor_data')
c.execute('ALTER TABLE sensor_data_new RENAME TO sensor_data')
conn.commit()

print("Migration complete. Only timestamp, fuel_level, and temperature are now in sensor_data.")

conn.close() 
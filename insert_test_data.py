import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/genset_monitoring.db')
c = conn.cursor()

base_time = datetime.strptime("2025-07-15 08:32:42", "%Y-%m-%d %H:%M:%S")
for i in range(1, 10):
    ts = (base_time + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
    fuel = 97.0 - i  # Example: decreasing fuel
    temp = 22.0 + i * 0.2  # Example: increasing temp
    c.execute("INSERT OR IGNORE INTO sensor_data (timestamp, fuel_level, temperature) VALUES (?, ?, ?)", (ts, fuel, temp))
conn.commit()
conn.close()
print("Inserted test data.") 
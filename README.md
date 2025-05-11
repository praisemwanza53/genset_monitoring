<<<<<<< HEAD
# GENSET\_MONITORING

## Overview

This project is a Streamlit-based dashboard for monitoring a genset (generator set) at a telecommunications site. It provides real-time monitoring of key sensor data such as fuel level, temperature, pressure, and GPS location. The dashboard includes:

* **Current Metrics**: Displays the latest readings for fuel level, temperature, and pressure.
* **Historical Charts**: Visualizes sensor data trends over time.
* **Alerts**: Flags unsafe sensor values that require attention.
* **GPS Map**: Shows the genset's location on an interactive map using Folium.
* **AI Predictions**: Uses the Gemini API to predict sensor health and recommend maintenance.

The app supports data input via manual entry, CSV/JSON file uploads, and JSON data input for integration with external systems.

## Project Structure

```
GENSET_MONITORING/
│
├── dashboard.py          # Main Streamlit app
├── dashboard1.py         # Alternative dashboard (if used)
├── config.py             # Configuration settings (e.g., TITLE, LOG_DIR)
├── components/           # Modular components for the app
│   ├── charts.py         # Functions for plotting time-series charts
│   └── alerts.py         # Functions for generating alerts
├── logs/                 # Directory for logs and database
│   ├── genset_data.db    # SQLite database storing sensor_data table
│   └── sensor_data.json  # Sample JSON data for testing
├── requirements.txt      # Dependencies for the project
├── simulate.py           # Script for simulating sensor data (if used)
└── README.md             # This file
```

## Prerequisites

* **Python**: Version 3.7 or higher
* **Virtual Environment**: Recommended for dependency management
* **Google Gemini API Key**: Required for AI predictions (set in `.env` or environment variables)

## Setup Instructions

### Clone the Repository (if applicable):

```bash
git clone <repository-url>
cd GENSET_MONITORING
```

### Create and Activate a Virtual Environment:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On macOS/Linux
```

### Install Dependencies:

```bash
pip install -r requirements.txt
```

### Set Up the Gemini API Key:

1. Obtain an API key from Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Set the key in your environment:

**On Windows**

```bash
set GEMINI_API_KEY=your-api-key
```

**On macOS/Linux**

```bash
export GEMINI_API_KEY=your-api-key
```

**Alternatively**, create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-api-key
```

### Run the Application:

```bash
streamlit run dashboard.py
```

The app will open in your default browser at `http://localhost:8501`.

## Usage

### Dashboard Features

**Sidebar Settings:**

* **Update Interval**: Adjust how often the dashboard refreshes (default: 30 seconds to avoid API rate limits).
* **Date Range**: Select the start and end dates for historical data.
* **Manual Data Input**: Enter sensor data (fuel level, temperature, pressure, latitude, longitude) manually.
* **JSON Input**: Paste JSON sensor data for quick updates.
* **File Upload**: Upload CSV or JSON files containing sensor data.

**Main Dashboard:**

* **Genset Status**: Toggle the genset ON/OFF (simulated).
* **Current Readings**: Displays the latest sensor values.
* **Historical Data**: Time-series charts for fuel level, temperature, and pressure.
* **Alerts**: Highlights unsafe sensor values.
* **Genset Location**: Interactive map showing the latest GPS coordinates.
* **AI Sensor Health Prediction**: Uses Gemini API to predict if maintenance is needed.

## Sample JSON Data

You can test the app with the following JSON data (found in `logs/sensor_data.json`):

```json
{
  "timestamp": "2025-05-11 00:56:41",
  "fuel_level": 58.455481074169185,
  "temperature": 109.74154493544458,
  "pressure": 45.7327093894346,
  "location": {"lat": -15.3875, "lon": 28.3228}
}
```

Copy this JSON into the "Update Sensor Data via JSON" section in the sidebar and click "Upload JSON Data". The map will display the location at `(-15.3875, 28.3228)`.

## Sample CSV Data

For CSV uploads, the file should have the following columns: `timestamp`, `fuel_level`, `temperature`, `pressure`. Optionally, include `latitude` and `longitude`.

**Example:**

```csv
timestamp,fuel_level,temperature,pressure,latitude,longitude
2025-05-11 00:56:41,58.5,109.7,45.7,-15.3875,28.3228
2025-05-11 00:57:41,58.0,110.0,46.0,-15.3876,28.3229
```

## Troubleshooting

**Gemini API 429 Error:**

* **Cause**: Exceeded API rate limits (e.g., 2 RPM on free tier).
* **Fix**: Increase the update interval to 30+ seconds, or upgrade to a paid Gemini API plan.
* **Details**: See the app's retry logic using `tenacity` for handling 429 errors.

**Database Errors:**

* **Cause**: Missing latitude or longitude columns in `sensor_data` table.
* **Fix**: The `db_init` function in `dashboard.py` automatically adds these columns on startup.

**Duplicate Key Errors:**

* **Cause**: Streamlit elements with duplicate keys.
* **Fix**: The app now uses unique keys for all elements.

## Dependencies

Key dependencies include:

* `streamlit==1.44.0`
* `pandas==2.2.3`
* `google-generativeai==0.8.3`
* `streamlit-folium==0.25.0`
* `folium==0.18.0`
* `tenacity==9.0.0` (for API retry logic)

See `requirements.txt` for the full list.

## Contributing

Feel free to fork this project, submit pull requests, or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.
=======
# IoT Genset Monitor (Streamlit App)

## Description

This project is a Streamlit web application designed to monitor key parameters of an Internet of Things (IoT) enabled generator set (Genset). It simulates reading sensor data (Fuel Level, Temperature, Pressure), stores this data persistently in an SQLite database, and provides a user interface to visualize current and historical readings, check for alerts, and simulate control actions (turning the Genset ON/OFF).

The application is currently set up for demonstration using dummy data generation but is structured to be adapted for real sensor input and hardware control. The monitoring context includes a specific location: Kitwe, Zambia.

## Features

* **Dashboard Display:** Shows the latest readings for Fuel Level (%), Temperature (°C), and Pressure (psi).
* **Historical Data Visualization:** Plots sensor readings over time using interactive Plotly charts.
* **Date Range Filtering:** Allows users to select a start and end date in the sidebar to view historical data for specific periods.
* **Database Storage:** Uses SQLite (`genset_data.db` located in `logs/`) for persistent storage of time-series sensor data.
* **Alert System:** Checks the latest readings against predefined thresholds (configurable in `src/components/alerts.py`) and displays warnings (e.g., Low Fuel, High Temperature).
* **Simulated Control:** Buttons to simulate turning the Genset ON or OFF (requires integration with actual hardware control logic).
* **Dummy Data Generation:** Includes a button to manually generate and store simulated sensor data for testing and demonstration.
* **AI Prediction Placeholder:** Includes a dedicated section in the UI prepared for integrating an AI/ML model to predict future fuel levels.


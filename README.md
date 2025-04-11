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

## File Structure

Based on the project layout:

GENSET_MONITORING/├── data/                     # Directory for raw data (if any)├── env/                      # Directory for environment files (e.g., virtual env)├── logs/                     # Directory for logs and database│   ├── genset_data.db        # SQLite database file│   └── sensor_data.json      # (Potentially obsolete JSON file)├── models/                   # Directory for trained AI/ML models├── reports/                  # Directory for generated reports├── src/                      # Source code directory│   ├── pycache/          # Python cache files (auto-generated)│   ├── components/           # Directory for UI/logic components│   │   ├── pycache/│   │   ├── init.py       # Makes 'components' a Python package│   │   ├── alerts.py         # Alert checking logic and thresholds│   │   └── charts.py         # Time series plotting function│   ├── utils/                # Directory for utility functions (if any)│   ├── config.py             # Configuration file (TITLE, LOG_DIR)│   ├── dashboard.py          # Main Streamlit application script│   ├── dashboard1.py         # (Another/alternative dashboard version?)│   └── simulate.py           # (Script for data simulation?)├── .gitignore                # Specifies intentionally untracked files for Git├── README.md                 # This file└── requirements.txt          # Python dependencies
## Installation & Setup

1.  **Clone the Repository (Optional):** If you have the code in a repository:
    ```bash
    git clone <your-repo-url>
    cd GENSET_MONITORING # Navigate into the project directory
    ```
    Otherwise, ensure you have the project files arranged according to the structure above.

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv env  # Creates the virtual environment in the 'env' directory
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3.  **Install Dependencies:** Ensure your `requirements.txt` file is up-to-date with at least:
    ```txt
    # requirements.txt
    streamlit
    pandas
    plotly
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Streamlit App:** Make sure you are in the main project directory (`GENSET_MONITORING`) and run:
    ```bash
    streamlit run src/dashboard.py
    ```
    This command targets the main application script inside the `src` directory. The app should open automatically in your web browser.

2.  **Interact with the App:**
    * View the current metrics and Genset status on the main page.
    * Use the sidebar to:
        * Select a **Start Date** and **End Date** to filter the historical data shown in the charts.
        * Click **"Generate & Store Dummy Data Point"** to add new simulated data to the database and refresh the view.
        * Adjust the (currently inactive) **Update Interval** slider.
    * Use the **"Turn Genset ON" / "Turn Genset OFF"** buttons to simulate control actions.
    * Observe the **Alerts** section for any threshold breaches based on the latest data.
    * Check the **Historical Data** charts for trends.
    * Note the **AI Fuel Level Prediction** section, which currently shows recent data and awaits model integration.

## Configuration

* **Application Title & Log Directory:** Modify the `TITLE` and `LOG_DIR` variables in `src/config.py`.
* **Alert Thresholds:** Adjust the threshold constants (e.g., `FUEL_LOW_THRESHOLD`, `TEMP_HIGH_THRESHOLD`) within the `src/components/alerts.py` file.

## Future Enhancements

* **Real Sensor Integration:** Replace dummy data generation (potentially in `src/simulate.py` or triggered within `src/dashboard.py`) with code to read data from actual IoT sensors.
* **Hardware Control:** Implement the actual logic within the ON/OFF button handlers in `src/dashboard.py` to send commands to the Genset control unit.
* **AI Model Integration:** Develop and integrate a machine learning model (loading from `models/`) in the "AI Fuel Level Prediction" section of `src/dashboard.py`.
* **User Authentication:** Add user login if needed for access control.
* **Enhanced Configuration:** Move thresholds or other settings to a more formal configuration file or environment variables.
* **Improved Auto-Refresh:** Implement a more robust auto-refresh mechanism in `src/dashboard.py` if near real-time updates without manual interaction are critical.
* **Utilize `utils/`:** Develop and use shared utility functions in the `src/utils/` directory.
* **Reporting:** Implement report generation features, potentially saving outputs to the `reports/` directory.


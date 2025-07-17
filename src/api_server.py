#!/usr/bin/env python3
"""
API Server for ESP32 Genset Monitoring
Provides HTTP endpoints for ESP32 to send sensor data and receive commands
"""

import json
import sqlite3
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.database import init_database, insert_sensor_data, get_latest_data

# Define DB_FILE for database path
DB_FILE = os.environ.get("DATABASE_PATH", os.path.join(os.getcwd(), "logs", "genset_data.db"))

# --- In-memory state for relay and buzzer commands ---
relay_state = False  # False=OFF, True=ON
buzzer_alert = False # True if AI alert should trigger buzzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_database()

def get_all_sensor_data(limit: int = 100) -> list:
    """Fetch up to 'limit' most recent sensor data records from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, temperature, fuel_level
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'timestamp': row[0],
                'temperature': row[1],
                'fuel_level': row[2],
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching all sensor data: {e}")
        return []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'database_path': DB_FILE
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sensor-data/all', methods=['GET'])
def get_all_sensor_data_endpoint():
    """
    Return up to 100 most recent sensor data records (for dashboard/history).
    Optional query param: ?limit=50
    """
    try:
        limit = int(request.args.get('limit', 100))
        data = get_all_sensor_data(limit=limit)
        return jsonify({'data': data, 'count': len(data)}), 200
    except Exception as e:
        logger.error(f"Error in /api/sensor-data/all: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor-data', methods=['GET', 'POST'])
def handle_sensor_data():
    """
    Handle sensor data:
    - POST: Receive sensor data from ESP32 and store in DB.
    - GET: Return the latest sensor data for the dashboard.
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
            # Extract sensor data
            temperature = data.get('temperature', 0)
            fuel_level = data.get('fuel_level', 0)
            # Store in DB
            insert_sensor_data(temperature, fuel_level, datetime.now())
            logger.info(f"Received sensor data: temp={temperature}°C, fuel={fuel_level}%")
            return jsonify({'status': 'success', 'message': 'Data received and stored', 'timestamp': datetime.now().isoformat()}), 200
        except Exception as e:
            logger.error(f"Error receiving sensor data: {e}")
            return jsonify({'error': str(e)}), 500
    
    if request.method == 'GET':
        try:
            latest_data = get_latest_data()
            if latest_data:
                return jsonify(latest_data), 200
            else:
                return jsonify({'message': 'No sensor data available yet.'}), 404
        except Exception as e:
            logger.error(f"Error retrieving sensor data: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Return relay/buzzer commands for ESP32."""
    return jsonify({
        'relay': 'on' if relay_state else 'off',
        'buzzer': buzzer_alert
    })

@app.route('/api/relay', methods=['POST'])
def set_relay():
    """Set relay state from dashboard/AI."""
    global relay_state
    req = request.get_json()
    state = req.get('state', '').lower()
    if state == 'on':
        relay_state = True
    elif state == 'off':
        relay_state = False
    else:
        return jsonify({'error': 'Invalid state'}), 400
    return jsonify({'status': 'success', 'relay': 'on' if relay_state else 'off'})

@app.route('/api/buzzer', methods=['POST'])
def set_buzzer():
    """Trigger buzzer alert from dashboard/AI (sets flag for ESP32 to buzz 2x on next poll)."""
    global buzzer_alert
    buzzer_alert = True
    return jsonify({'status': 'success', 'buzzer': True})

# --- ESP32 should reset buzzer_alert after buzzing ---
@app.route('/api/buzzer/reset', methods=['POST'])
def reset_buzzer():
    """Reset buzzer alert flag after ESP32 buzzes."""
    global buzzer_alert
    buzzer_alert = False
    return jsonify({'status': 'success', 'buzzer': False})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status."""
    try:
        # Get latest sensor data
        latest_data = get_latest_data()
        
        if latest_data:
            return jsonify({
                'status': 'online',
                'last_update': latest_data['timestamp'],
                'sensor_data': {
                    'temperature': latest_data['temperature'],
                    'fuel_level': latest_data['fuel_level'],
                }
            }), 200
        else:
            return jsonify({
                'status': 'no_data',
                'message': 'No sensor data available'
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration."""
    try:
        return jsonify({
            'database_path': DB_FILE,
            'groq_api_configured': bool(GROQ_API_KEY),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for ESP32 connectivity."""
    return jsonify({
        'message': 'API server is running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/health',
            '/api/sensor-data',
            '/api/buzzer',
            '/api/status',
            '/api/config',
            '/api/test'
        ]
    }), 200

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting API server...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /api/sensor-data - Receive sensor data")
    logger.info("  POST /api/buzzer - Control buzzer")
    logger.info("  GET  /api/status - Get system status")
    logger.info("  GET  /api/config - Get configuration")
    logger.info("  GET  /api/test - Test endpoint")
    
    # Run the server
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,        # Default Flask port
        debug=False       # Disable debug mode for production
    ) 
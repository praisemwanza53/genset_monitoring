# Genset Monitoring System - Deployment Guide

This guide covers deploying both the Streamlit dashboard and the API server for ESP32 communication.

## System Overview

The genset monitoring system consists of:
- **Streamlit Dashboard**: Web interface for monitoring and control
- **API Server**: HTTP endpoints for ESP32 communication
- **ESP32 Device**: Hardware for sensor data collection

## Prerequisites

- Python 3.8+
- ESP32 development board
- Required sensors (temperature, fuel level, humidity, GPS)
- Internet connection for hosted deployment

## Local Deployment

### 1. Setup Environment

```bash
# Clone or download the project
cd genset_monitoring

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r api_requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_PATH=data/genset_monitoring.db
```

### 3. Start the API Server

```bash
# Option 1: Direct start
python api_server.py

# Option 2: Using startup script
python start_api_server.py
```

The API server will start on `http://localhost:5000`

### 4. Start the Streamlit Dashboard

```bash
streamlit run src/dashboard.py
```

The dashboard will be available at `http://localhost:8501`

### 5. Configure ESP32

Update the ESP32 code with your local IP address:

```cpp
const char* serverUrl = "http://YOUR_LOCAL_IP:5000";
```

## Hosted Deployment

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/genset_monitoring.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set environment variables:
     - `GROQ_API_KEY`: Your Groq API key
   - Deploy

3. **Update ESP32 for Hosted URL**:
   ```cpp
   const char* serverUrl = "https://your-app-name.streamlit.app";
   ```

### Option 2: Heroku

1. **Create Heroku App**:
   ```bash
   heroku create your-genset-monitoring-app
   ```

2. **Add Buildpacks**:
   ```bash
   heroku buildpacks:add heroku/python
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set GROQ_API_KEY=your_groq_api_key
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 3: Railway

1. **Connect GitHub Repository**:
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Set Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API key

3. **Deploy**:
   - Railway will automatically deploy from your repository

## API Endpoints

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/sensor-data` | POST | Receive sensor data |
| `/api/buzzer` | POST | Control buzzer |
| `/api/status` | GET | Get system status |
| `/api/config` | GET | Get configuration |
| `/api/test` | GET | Test endpoint |

### Example Usage

**Send Sensor Data**:
```bash
curl -X POST http://localhost:5000/api/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 25.5,
    "fuel_level": 75.2,
    "humidity": 60.1,
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

**Control Buzzer**:
```bash
curl -X POST http://localhost:5000/api/buzzer \
  -H "Content-Type: application/json" \
  -d '{
    "action": "beep",
    "duration": 2000
  }'
```

## ESP32 Configuration

### WiFi Setup

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### Server Configuration

For local deployment:
```cpp
const char* serverUrl = "http://YOUR_LOCAL_IP:5000";
```

For hosted deployment:
```cpp
const char* serverUrl = "https://your-app-url.com";
```

### Sensor Configuration

Update sensor pins in the ESP32 code:
```cpp
#define TEMP_SENSOR_PIN 4
#define FUEL_SENSOR_PIN 5
#define HUMIDITY_SENSOR_PIN 6
#define BUZZER_PIN 7
```

## Troubleshooting

### Common Issues

1. **ESP32 Connection Failed**:
   - Check WiFi credentials
   - Verify server URL is correct
   - Ensure server is running

2. **API Server Won't Start**:
   - Check if port 5000 is available
   - Verify dependencies are installed
   - Check logs in `logs/api_server.log`

3. **Dashboard Issues**:
   - Verify Streamlit is installed
   - Check database file permissions
   - Ensure environment variables are set

### Debug Commands

**Test API Server**:
```bash
curl http://localhost:5000/health
```

**Test ESP32 Connection**:
```bash
curl http://localhost:5000/api/test
```

**Check Database**:
```bash
python src/check_db.py
```

## Security Considerations

1. **API Security**:
   - Use HTTPS for hosted deployments
   - Implement authentication if needed
   - Rate limit API endpoints

2. **Network Security**:
   - Use strong WiFi passwords
   - Consider VPN for remote access
   - Monitor network traffic

3. **Data Security**:
   - Encrypt sensitive data
   - Regular database backups
   - Secure API keys

## Monitoring and Maintenance

### Log Files

- API Server: `logs/api_server.log`
- Streamlit: Check terminal output
- ESP32: Serial monitor

### Database Management

```bash
# Check database status
python src/check_db.py

# Migrate database
python src/migrate_db.py

# Backup database
cp data/genset_monitoring.db backup/
```

### Performance Monitoring

- Monitor API response times
- Check database size
- Monitor ESP32 battery level
- Track sensor accuracy

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files
3. Test individual components
4. Verify network connectivity

## Next Steps

1. **Customization**: Modify sensor types and thresholds
2. **Scaling**: Add multiple ESP32 devices
3. **Advanced Features**: Implement machine learning predictions
4. **Mobile App**: Create companion mobile application 
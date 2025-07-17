# ESP32 Genset Monitor Setup Guide

## Prerequisites

### Hardware Required
- ESP32 Development Board
- BME280 Temperature/Humidity Sensor
- GPS Module (NEO-6M or similar)
- Fuel Level Sensor (Analog)
- Buzzer Module
- LED (for status indication)
- Jumper wires and breadboard

### Software Required
- Arduino IDE
- Required Libraries (install via Library Manager):
  - WiFi
  - HTTPClient
  - ArduinoJson (by Benoit Blanchon)
  - Adafruit BME280 Library
  - TinyGPS++

## Hardware Connections

### ESP32 Pin Connections
```
BME280 Sensor:
- VCC → 3.3V
- GND → GND
- SDA → GPIO21
- SCL → GPIO22

GPS Module:
- VCC → 3.3V
- GND → GND
- TX → GPIO16 (GPS_RX)
- RX → GPIO17 (GPS_TX)

Fuel Sensor:
- VCC → 3.3V
- GND → GND
- Signal → GPIO34 (FUEL_SENSOR_PIN)

Buzzer:
- VCC → 3.3V
- GND → GND
- Signal → GPIO25 (BUZZER_PIN)

LED:
- Anode → GPIO2 (LED_PIN)
- Cathode → GND (with 220Ω resistor)
```

## Configuration Steps

### 1. Update WiFi Settings
In `ESP32_Genset_Monitor.ino`, update these lines:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### 2. Update Streamlit App URL
Replace the placeholder with your actual hosted Streamlit app URL:
```cpp
const char* streamlit_host = "your-streamlit-app-url.com";  // Your actual URL
const int streamlit_port = 443;  // Use 443 for HTTPS, 80 for HTTP
```

### 3. Configure Sensor Calibration
Adjust fuel sensor calibration based on your specific sensor:
```cpp
const float fuel_empty_voltage = 0.5;  // Voltage when fuel tank is empty
const float fuel_full_voltage = 3.3;   // Voltage when fuel tank is full
```

## Deployment Options

### Option 1: Local Network (Same WiFi)
If your ESP32 and computer are on the same WiFi network:
1. Find your computer's local IP address
2. Update `streamlit_host` to your computer's IP
3. Set `streamlit_port` to 8501 (Streamlit default)

### Option 2: Hosted Streamlit App
For a hosted Streamlit app (Streamlit Cloud, Heroku, etc.):
1. Deploy your Streamlit app to a hosting service
2. Update `streamlit_host` to your hosted URL
3. Ensure your app has the `/api/data` and `/api/buzzer` endpoints

### Option 3: Port Forwarding
If using a local Streamlit app with port forwarding:
1. Configure your router to forward port 8501 to your computer
2. Use your public IP address as `streamlit_host`
3. Set `streamlit_port` to 8501

## Testing the Connection

### 1. Serial Monitor
Open Arduino IDE Serial Monitor (115200 baud) to see:
- WiFi connection status
- Data transmission logs
- Error messages

### 2. Expected Serial Output
```
Connecting to WiFi: YOUR_WIFI_SSID
........
WiFi connected!
IP address: 192.168.1.100
ESP32 Genset Monitor initialized
Sending data to: http://your-streamlit-app-url.com:443/api/data
Sending JSON: {"device_id":"ESP32_GENSET_001","timestamp":1234567,"fuel_level":75.5,"temperature":25.3,"humidity":60.2,"latitude":0.0,"longitude":0.0,"altitude":0.0}
HTTP Response code: 200
Response: {"status":"success"}
```

## Troubleshooting

### Common Issues

1. **WiFi Connection Failed**
   - Check SSID and password
   - Ensure WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
   - Check signal strength

2. **HTTP Connection Failed**
   - Verify the Streamlit app URL is correct
   - Check if the app is running and accessible
   - Ensure firewall allows the connection

3. **Sensor Reading Errors**
   - Check wiring connections
   - Verify sensor addresses (BME280 typically 0x76)
   - Calibrate fuel sensor voltage range

4. **GPS Not Working**
   - Ensure GPS module has clear sky view
   - Check baud rate (9600)
   - Verify TX/RX connections

### Debug Mode
Add this to the loop() function for detailed debugging:
```cpp
void loop() {
  // Add debug prints
  Serial.print("Fuel Level: ");
  Serial.println(readFuelLevel());
  Serial.print("Temperature: ");
  Serial.println(readTemperature());
  Serial.print("Humidity: ");
  Serial.println(readHumidity());
  
  // ... rest of the loop
}
```

## Security Considerations

1. **WiFi Security**: Use WPA2 or WPA3 encryption
2. **HTTPS**: Use HTTPS for hosted apps when possible
3. **API Keys**: Consider adding authentication to your endpoints
4. **Network Isolation**: Consider using a dedicated network for IoT devices

## Power Requirements

- ESP32: 3.3V, ~200mA peak
- BME280: 3.3V, ~1mA
- GPS Module: 3.3V, ~25mA
- Buzzer: 3.3V, ~20mA
- Total: ~250mA peak

Use a stable 3.3V power supply capable of 500mA or more.

## Maintenance

1. **Regular Calibration**: Recalibrate fuel sensor monthly
2. **Firmware Updates**: Keep Arduino libraries updated
3. **Hardware Inspection**: Check connections periodically
4. **Log Monitoring**: Monitor serial output for errors

## Advanced Configuration

### Custom Data Interval
Change the data transmission frequency:
```cpp
const unsigned long DATA_SEND_INTERVAL = 60000; // 1 minute
```

### Custom Buzzer Duration
Adjust buzzer alert duration:
```cpp
const unsigned long BUZZER_DURATION = 10000; // 10 seconds
```

### Multiple Devices
For multiple gensets, change the device ID:
```cpp
const String device_id = "ESP32_GENSET_002";
``` 
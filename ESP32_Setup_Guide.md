# ESP32 Genset Monitor Setup Guide

## Prerequisites

### Hardware Required
- ESP32 Development Board
- LM75 Temperature Sensor (I2C)
- Ultrasonic Sensor (HC-SR04 or similar) for fuel level
- Buzzer Module
- Relay Module
- OLED Display (SSD1306, 128x64)
- Jumper wires and breadboard

### Software Required
- Arduino IDE
- Required Libraries (install via Library Manager):
  - WiFi
  - HTTPClient
  - Wire (I2C)
  - Adafruit SSD1306 Library
  - Adafruit GFX Library

## Hardware Connections

### ESP32 Pin Connections
```
LM75 Temperature Sensor (I2C):
- VCC → 3.3V
- GND → GND
- SDA → GPIO21
- SCL → GPIO22

Ultrasonic Sensor (HC-SR04):
- VCC → 3.3V
- GND → GND
- TRIG → GPIO12
- ECHO → GPIO14

OLED Display (SSD1306):
- VCC → 3.3V
- GND → GND
- SDA → GPIO21 (shared with LM75)
- SCL → GPIO22 (shared with LM75)

Buzzer:
- VCC → 3.3V
- GND → GND
- Signal → GPIO26

Relay:
- VCC → 3.3V
- GND → GND
- Signal → GPIO27
```

## Configuration Steps

### 1. Update WiFi Settings
In `ESP32_Genset_Monitor.ino`, update these lines:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### 2. Update API Server URL
Configure the API server URL for your deployment:
```cpp
// Set to 1 for local, 0 for hosted
#define USE_LOCAL_API 0

#if USE_LOCAL_API
const char* api_server_url_data = "http://YOUR_LOCAL_IP:5000/api/sensor-data";
const char* api_server_url_cmds = "http://YOUR_LOCAL_IP:5000/api/commands";
#else
const char* api_server_url_data = "https://genset-monitoring.onrender.com/api/sensor-data";
const char* api_server_url_cmds = "https://genset-monitoring.onrender.com/api/commands";
#endif
```

### 3. Configure Sensor Calibration
Adjust ultrasonic sensor calibration based on your fuel tank:
```cpp
// In getFuelLevel() function, adjust these values:
int fuelLevel = map((int)distance, 10, 40, 100, 0);
// 10cm = full tank, 40cm = empty tank
// Adjust these values based on your tank's actual dimensions
```

## Deployment Options

### Option 1: Local Network (Same WiFi)
If your ESP32 and computer are on the same WiFi network:
1. Find your computer's local IP address
2. Update `api_server_url_data` and `api_server_url_cmds` to your computer's IP
3. Set `USE_LOCAL_API` to 1

### Option 2: Hosted API Server
For a hosted API server (Render, Heroku, etc.):
1. Deploy your API server to a hosting service
2. Update the API URLs to your hosted server URL
3. Set `USE_LOCAL_API` to 0

## Testing the Connection

### 1. Serial Monitor
Open Arduino IDE Serial Monitor (115200 baud) to see:
- WiFi connection status
- Sensor readings
- Data transmission logs
- Error messages

### 2. Expected Serial Output
```
Connecting to WiFi: YOUR_WIFI_SSID
........
✅ WiFi Connected!
IP Address: 192.168.1.100
🌐 Web server started
🌡 Temp: 25.5 °C, ⛽ Fuel: 75 %
Sending payload: {"temperature":25.5,"fuel_level":75}
HTTP Response: 200
Response: {"status":"success","message":"Data received and stored"}
```

### 3. Local Web Interface
The ESP32 serves a local web interface accessible at its IP address:
- `http://ESP32_IP/` — Status message
- `http://ESP32_IP/sensors` — Get current sensor readings (JSON)
- `http://ESP32_IP/relay/on` — Turn relay ON
- `http://ESP32_IP/relay/off` — Turn relay OFF
- `http://ESP32_IP/notify` — Trigger buzzer

## Troubleshooting

### Common Issues

1. **WiFi Connection Failed**
   - Check SSID and password
   - Ensure WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
   - Check signal strength

2. **HTTP Connection Failed**
   - Verify the API server URL is correct
   - Check if the API server is running and accessible
   - Ensure firewall allows the connection

3. **Sensor Reading Errors**
   - **LM75:** Check I2C connections and address (default 0x48)
   - **Ultrasonic:** Verify TRIG/ECHO connections and power supply
   - **OLED:** Check I2C connections and address (default 0x3C)

4. **I2C Issues**
   - Ensure proper pull-up resistors on SDA/SCL lines
   - Check for address conflicts between LM75 and OLED
   - Verify Wire.begin() is called with correct pins

### Debug Mode
Add this to the loop() function for detailed debugging:
```cpp
void loop() {
  // Add debug prints
  Serial.print("Temperature: ");
  Serial.println(temp);
  Serial.print("Fuel Level: ");
  Serial.println(fuel);
  Serial.print("WiFi Status: ");
  Serial.println(WiFi.status());
  
  // ... rest of the loop
}
```

## Security Considerations

1. **WiFi Security**: Use WPA2 or WPA3 encryption
2. **HTTPS**: Use HTTPS for hosted API servers when possible
3. **Network Isolation**: Consider using a dedicated network for IoT devices
4. **Local Access**: The ESP32 web server is accessible to anyone on the same network

## Power Requirements

- ESP32: 3.3V, ~200mA peak
- LM75: 3.3V, ~1mA
- Ultrasonic Sensor: 3.3V, ~15mA
- OLED Display: 3.3V, ~20mA
- Buzzer: 3.3V, ~20mA
- Relay: 3.3V, ~70mA
- Total: ~330mA peak

Use a stable 3.3V power supply capable of 500mA or more.

## Maintenance

1. **Regular Calibration**: Recalibrate ultrasonic sensor if fuel tank dimensions change
2. **Firmware Updates**: Keep Arduino libraries updated
3. **Hardware Inspection**: Check connections periodically
4. **Log Monitoring**: Monitor serial output for errors

## Advanced Configuration

### Custom Data Interval
Change the data transmission frequency:
```cpp
// In loop() function, change the delay:
delay(3000); // 3 seconds (current)
// delay(5000); // 5 seconds
// delay(10000); // 10 seconds
```

### Custom Buzzer Duration
Adjust buzzer alert duration:
```cpp
// In buzz() function:
void buzz(int times, int duration = 700, int gap = 400) {
  // duration = buzzer on time (ms)
  // gap = buzzer off time (ms)
}
```

### Multiple Devices
For multiple gensets, change the device identification:
```cpp
// Add a device ID variable:
const String device_id = "ESP32_GENSET_001";
```

### OLED Display Customization
Modify the display layout in `displaySensorData()`:
```cpp
void displaySensorData(float temp, int fuel) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // Customize text position and content
  display.setCursor(0, 0);
  display.print("Temp: ");
  display.print(temp);
  display.println(" C");
  
  display.print("Fuel: ");
  display.print(fuel);
  display.println(" %");
  
  display.display();
}
``` 
# ESP32 Connection Troubleshooting Guide

## 🔧 **Common ESP32 Connection Issues**

### **1. ESP32 Not Responding**
**Symptoms:** "Connection timeout" or "Connection refused" errors

**Solutions:**
- ✅ Check if ESP32 is powered on
- ✅ Verify ESP32 is connected to WiFi network
- ✅ Check ESP32 Serial Monitor for IP address and status
- ✅ Ensure ESP32 code is uploaded and running
- ✅ Check if ESP32 is on the same network as your API server

### **2. Wrong API Server URL**
**Symptoms:** ESP32 fails to send data, dashboard shows no updates

**Solutions:**
- ✅ Check API server URL in ESP32 code
- ✅ Ensure API server is running and reachable
- ✅ Check firewall settings

### **3. Sensor Reading Errors**
**Symptoms:** Temperature or fuel level readings are missing or incorrect

**Solutions:**
- ✅ Check wiring for NTC thermistor and ultrasonic sensor
- ✅ Calibrate sensors in code if needed
- ✅ Monitor Serial output for sensor errors

### **4. HTTP Connection Issues**
**Symptoms:** ESP32 cannot POST data to API server

**Solutions:**
- ✅ Verify API server URL and port
- ✅ Ensure API server is accessible from ESP32's network
- ✅ Check for HTTP 200 response in Serial Monitor

## 🛠️ **Testing Steps**

### **Step 1: Basic Connectivity**
1. Open Arduino IDE Serial Monitor
2. ESP32 should print WiFi connection and IP address
3. Look for "Sending data to: ..." and HTTP response code

### **Step 2: Data Verification**
1. Check API server logs for received data
2. Use dashboard to view latest readings
3. Data should include only `temperature` and `fuel_level`

## 🔄 **Simulation Mode**

If ESP32 is not available, you can:
1. Use dashboard's test/simulate data features (if available)
2. This will create realistic sensor data for testing
3. Charts will work with simulated data

## 📱 **ESP32 Code Verification**

Make sure your ESP32 code includes:
```cpp
// Required endpoints
server.on("/", []() { server.send(200, "text/plain", "ESP32 is running."); });
server.on("/sensors", handleSensorData); // Sensor data
server.on("/relay/on", handleRelayOn);   // Relay control
server.on("/relay/off", handleRelayOff); // Relay control  
server.on("/notify", handleNotification); // Buzzer control
```

## 🌐 **Network Configuration**

**For ESP32:**
- WiFi SSID: (your network)
- WiFi Password: (your password)
- API server URL: (your API server address)

**For Dashboard:**
- Set API server URL in sidebar
- Ensure dashboard can reach API server

## 📊 **Debug Information**

- Serial Monitor shows WiFi, sensor, and HTTP status
- API server logs show received data
- Dashboard displays latest and historical readings

## 🚨 **Emergency Testing**

If ESP32 is completely unavailable:
1. Use dashboard's test/simulate data features (if available)
2. Test all dashboard features with simulated data 
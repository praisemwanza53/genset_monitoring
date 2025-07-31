#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>
#include <math.h>

// Wi-Fi credentials
const char* ssid = "";
const char* password = "";

// API endpoints
#define USE_LOCAL_API 0
#if USE_LOCAL_API
const char* api_server_url_data = "http://192.168.100.14:5000/api/sensor-data";
const char* api_server_url_cmds = "http://192.168.100.14:5000/api/commands";
#else
const char* api_server_url_data = "https://genset-monitoring.onrender.com/api/sensor-data";
const char* api_server_url_cmds = "https://genset-monitoring.onrender.com/api/commands";
#endif

// Sensor Pins
#define TRIG_PIN 12
#define ECHO_PIN 14
#define RELAY_PIN 27
#define BUZZER_PIN 26

// OLED settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Web server
WebServer server(80);
bool wasWiFiConnected = false;

// LM75 settings
#define LM75_ADDR 0x48
#define SDA_PIN 21
#define SCL_PIN 22

// ---------------- BUZZER FUNCTION ----------------
void buzz(int times, int duration = 700, int gap = 400) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
    delay(gap);
  }
}

// ---------------- RELAY CONTROL ----------------
void handleRelayOn() {
  digitalWrite(RELAY_PIN, HIGH);
  server.send(200, "text/plain", "Relay ON");
}
void handleRelayOff() {
  digitalWrite(RELAY_PIN, LOW);
  server.send(200, "text/plain", "Relay OFF");
}
void handleNotification() {
  buzz(2, 700, 500);
  server.send(200, "text/plain", "Notification buzzed");
}

// ---------------- FUEL LEVEL ----------------
int getFuelLevel() {
  long duration;

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) {
    Serial.println("⚠️ No echo received");
    return 0;
  }

  float distance = duration * 0.034 / 2.0;
  if (distance < 2 || distance > 400) {
    Serial.println("⚠️ Distance out of range");
    return 0;
  }

  Serial.print("📏 Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  int fuelLevel = map((int)distance, 10, 40, 100, 0);
  fuelLevel = constrain(fuelLevel, 0, 100);
  return round(fuelLevel / 5.0) * 5;
}

// ---------------- LM75 TEMPERATURE ----------------
bool readLM75(float &tempC) {
  const int maxAttempts = 3;

  for (int attempt = 0; attempt < maxAttempts; attempt++) {
    Wire.beginTransmission(LM75_ADDR);
    Wire.write(0);
    if (Wire.endTransmission(false) != 0) {
      delay(20);
      continue;
    }

    Wire.requestFrom(LM75_ADDR, 2);
    if (Wire.available() == 2) {
      byte msb = Wire.read();
      byte lsb = Wire.read();
      int16_t rawTemp = ((msb << 8) | lsb) >> 7;
      tempC = rawTemp * 0.5;
      return true;
    }
    delay(20);
  }

  return false;
}

// ---------------- SENSOR DATA HANDLER ----------------
void handleSensorData() {
  float temp;
  bool tempRead = readLM75(temp);
  if (!tempRead) temp = 0.0;

  int fuel = getFuelLevel();
  if (fuel < 0 || fuel > 100) fuel = 0;

  String json = "{";
  json += "\"temperature\":" + String(temp) + ",";
  json += "\"fuel_level\":" + String(fuel);
  json += "}";
  server.send(200, "application/json", json);
}

// ---------------- PUSH TO API ----------------
void pushToApiServer(float temp, int fuel) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_server_url_data);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"temperature\":" + String(temp) + ",\"fuel_level\":" + String(fuel) + "}";
    Serial.print("Sending payload: ");
    Serial.println(payload);

    int httpResponseCode = http.POST(payload);
    Serial.print("HTTP Response: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error: " + http.errorToString(httpResponseCode));
    }

    http.end();
  }
}

// ---------------- FETCH REMOTE COMMANDS ----------------
void fetchRemoteActions() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_server_url_cmds);
    int httpCode = http.GET();

    if (httpCode == 200) {
      String payload = http.getString();
      Serial.println("Remote action: " + payload);

      if (payload.indexOf("\"relay\":\"on\"") >= 0) digitalWrite(RELAY_PIN, HIGH);
      else if (payload.indexOf("\"relay\":\"off\"") >= 0) digitalWrite(RELAY_PIN, LOW);

      if (payload.indexOf("\"buzzer\":true") >= 0) buzz(2, 700, 400);
    } else {
      Serial.println("⚠️ HTTP error: " + String(httpCode));
    }

    http.end();
  }
}

// ---------------- WIFI ----------------
void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    buzz(3, 500, 300);
    wasWiFiConnected = true;
  } else {
    Serial.println("\n❌ Failed to connect.");
    wasWiFiConnected = false;
    while (true);
  }
}

void checkWiFiReconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ Lost WiFi. Reconnecting...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);

    int attempt = 0;
    while (WiFi.status() != WL_CONNECTED && attempt < 20) {
      delay(1000);
      Serial.print(".");
      attempt++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ Reconnected to WiFi!");
      Serial.print("📶 IP: ");
      Serial.println(WiFi.localIP());
      buzz(3, 500, 300);
      wasWiFiConnected = true;
    } else {
      Serial.println("\n❌ Still not connected.");
      wasWiFiConnected = false;
    }
  }
}

// ---------------- OLED ----------------
void displaySensorData(float temp, int fuel) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.print("Temp: ");
  display.print(temp);
  display.println(" C");

  display.print("Fuel: ");
  display.print(fuel);
  display.println(" %");

  display.display();
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN, 50000);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  buzz(4, 1000, 500);

  connectToWiFi();

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("❌ OLED init failed");
    while (true);
  }

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("ESP32 Starting...");
  display.display();
  delay(2000);

  server.on("/", []() {
    server.send(200, "text/plain", "ESP32 is running.");
  });
  server.on("/relay/on", handleRelayOn);
  server.on("/relay/off", handleRelayOff);
  server.on("/sensors", handleSensorData);
  server.on("/notify", handleNotification);
  server.begin();
  Serial.println("🌐 Web server started");
}

// ---------------- LOOP ----------------
void loop() {
  server.handleClient();
  checkWiFiReconnect();

  float temp;
  if (!readLM75(temp)) temp = 0.0;
  int fuel = getFuelLevel();

  Serial.print("🌡 Temp: ");
  Serial.print(temp);
  Serial.print(" °C, ⛽ Fuel: ");
  Serial.print(fuel);
  Serial.println(" %");

  displaySensorData(temp, fuel);
  pushToApiServer(temp, fuel);
  fetchRemoteActions();

  delay(3000);
}

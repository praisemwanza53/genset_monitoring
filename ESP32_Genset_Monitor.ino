#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
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
#define NTC_PIN 32
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

// Track WiFi status
bool wasWiFiConnected = false;

// --- BUZZER FUNCTION ---
void buzz(int times, int duration = 700, int gap = 400) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
    delay(gap);
  }
}

// --- RELAY CONTROL HANDLERS ---
void handleRelayOn() {
  digitalWrite(RELAY_PIN, HIGH);
  server.send(200, "text/plain", "Relay ON");
}
void handleRelayOff() {
  digitalWrite(RELAY_PIN, LOW);
  server.send(200, "text/plain", "Relay OFF");
}

// --- BUZZER ALERT ---
void handleNotification() {
  buzz(2, 700, 500);
  server.send(200, "text/plain", "Notification buzzed");
}

// --- FUEL LEVEL CALCULATION ---
int getFuelLevel() {
  long duration;

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH, 30000);  // Timeout at 30ms

  if (duration == 0) {
    Serial.println("⚠️ No echo received");
    return 0;
  }

  float distance = duration * 0.034 / 2.0;

  if (distance < 2 || distance > 400) {
    Serial.print("⚠️ Distance out of range: ");
    Serial.println(distance);
    return 0;
  }

  Serial.print("📏 Measured distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  int fuelLevel = map((int)distance, 10, 40, 100, 0);
  fuelLevel = constrain(fuelLevel, 0, 100);
  fuelLevel = round(fuelLevel / 5.0) * 5; // Round to nearest 5%

  return fuelLevel;
}

// --- NTC TEMPERATURE READING ---
float readNTCTemperature() {
  const float SERIES_RESISTOR = 10000.0;
  const float NOMINAL_RESISTANCE = 10000.0;
  const float NOMINAL_TEMPERATURE = 25.0;
  const float B_COEFFICIENT = 3950.0;
  const float ADC_MAX = 4095.0;
  const float SUPPLY_VOLTAGE = 3.3;

  int adcValue = analogRead(NTC_PIN);

  if (adcValue <= 0 || adcValue >= 4095) {
    Serial.println("⚠️ Invalid ADC value for NTC");
    return -100.0;
  }

  float voltage = adcValue * SUPPLY_VOLTAGE / ADC_MAX;
  float resistance = (voltage * SERIES_RESISTOR) / (SUPPLY_VOLTAGE - voltage); // Corrected formula

  if (resistance <= 0 || resistance > 1000000.0) {
    Serial.println("⚠️ Resistance out of range");
    return -99.0;
  }

  Serial.print("🔌 NTC ADC: ");
  Serial.print(adcValue);
  Serial.print(", V: ");
  Serial.print(voltage);
  Serial.print(" V, R: ");
  Serial.print(resistance);
  Serial.println(" Ohms");

  float steinhart;
  steinhart = resistance / NOMINAL_RESISTANCE;
  steinhart = log(steinhart);
  steinhart /= B_COEFFICIENT;
  steinhart += 1.0 / (NOMINAL_TEMPERATURE + 273.15);
  steinhart = 1.0 / steinhart;
  steinhart -= 273.15;

  return steinhart;
}

// --- SEND SENSOR DATA LOCALLY ---
void handleSensorData() {
  float temp = readNTCTemperature();
  int fuel = getFuelLevel();

  if (isnan(temp)) temp = 0.0;
  if (fuel < 0 || fuel > 100) fuel = 0;

  String json = "{";
  json += "\"temperature\":" + String(temp) + ",";
  json += "\"fuel_level\":" + String(fuel);
  json += "}";

  server.send(200, "application/json", json);
}

// --- PUSH TO API SERVER ---
void pushToApiServer(float temp, int fuel) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_server_url_data);
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"temperature\":" + String(temp) + ",";
    payload += "\"fuel_level\":" + String(fuel);
    payload += "}";

    Serial.print("Sending payload: ");
    Serial.println(payload);

    int httpResponseCode = http.POST(payload);
    Serial.print("HTTP Response: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.print("Error: ");
      Serial.println(http.errorToString(httpResponseCode));
    }

    http.end();
  }
}

// --- FETCH REMOTE ACTIONS ---
void fetchRemoteActions() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_server_url_cmds);
    int httpCode = http.GET();

    if (httpCode == 200) {
      String payload = http.getString();
      Serial.println("Remote action: " + payload);

      if (payload.indexOf("\"relay\":\"on\"") >= 0) {
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("✅ Relay: ON");
      } else if (payload.indexOf("\"relay\":\"off\"") >= 0) {
        digitalWrite(RELAY_PIN, LOW);
        Serial.println("✅ Relay: OFF");
      }

      if (payload.indexOf("\"buzzer\":true") >= 0) {
        buzz(2, 700, 400);
        Serial.println("✅ Buzzer activated remotely");
      }
    } else {
      Serial.print("⚠️ HTTP error: ");
      Serial.println(httpCode);
    }

    http.end();
  }
}

// --- WIFI CONNECTION ---
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
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✅ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    buzz(3, 500, 300);
    wasWiFiConnected = true;
  } else {
    Serial.println("❌ Failed to connect to WiFi.");
    wasWiFiConnected = false;
    while (true);
  }
}

// --- CHECK AND RECONNECT WIFI ---
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
      Serial.print("📶 New IP: ");
      Serial.println(WiFi.localIP());
      buzz(3, 500, 300);
      wasWiFiConnected = true;
    } else {
      Serial.println("\n❌ Still not connected.");
      wasWiFiConnected = false;
    }
  } else {
    wasWiFiConnected = true;
  }
}

// --- DISPLAY DATA ON OLED ---
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

// --- SETUP ---
void setup() {
  Serial.begin(115200);
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

// --- MAIN LOOP ---
void loop() {
  server.handleClient();
  checkWiFiReconnect();

  float temp = readNTCTemperature();
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

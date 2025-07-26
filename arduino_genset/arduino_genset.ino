const int DIGITAL_SENSOR_PIN = 2;  // Connect sensor's "F" output to this pin (must be interrupt-capable)
volatile unsigned long pulseCount = 0;
unsigned long lastMeasurementTime = 0;
const unsigned long MEASUREMENT_INTERVAL = 1000;  // 1-second measurement window

// CALIBRATION CONSTANTS (ADJUST THESE!)
const float A = 0.1;     // Slope (Hz/°C) - requires calibration
const float B = 25.0;    // Intercept (°C) - requires calibration

void setup() {
  Serial.begin(9600);
  pinMode(DIGITAL_SENSOR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(DIGITAL_SENSOR_PIN), countPulse, RISING);
}

void loop() {
  static unsigned long lastPrintTime = 0;
  
  if (millis() - lastMeasurementTime >= MEASUREMENT_INTERVAL) {
    // Capture and reset count
    noInterrupts();
    unsigned long currentCount = pulseCount;
    pulseCount = 0;
    interrupts();
    
    // Calculate frequency and temperature
    float frequency = currentCount * (1000.0 / MEASUREMENT_INTERVAL);
    float temperature = A * frequency + B;
    
    // Reset measurement timer
    lastMeasurementTime = millis();
    
    // Serial output every second
    Serial.print("Frequency: ");
    Serial.print(frequency);
    Serial.print(" Hz | Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");
  }
}

// Interrupt service routine
void countPulse() {
  pulseCount++;
}
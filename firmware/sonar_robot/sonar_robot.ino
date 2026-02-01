/*
  🎮 SONAR SYSTEM - Arduino Firmware
  For HC-SR04 Ultrasonic Sensor with Robot Control
  
  Hardware:
  - Arduino Uno/Nano or compatible
  - HC-SR04 Ultrasonic Sensor
  - L298N Motor Driver (or compatible)
  - 2x DC Motors
  
  Serial Protocol:
  - Output: "angle,distance" (e.g., "90,150")
  - Input Commands:
    - MODE:RADAR    - Switch to radar scanning mode
    - MODE:CONTROL  - Switch to manual control mode
    - M:F:speed     - Move forward at speed (0-255)
    - M:B:speed     - Move backward
    - M:L:speed     - Turn left
    - M:R:speed     - Turn right
    - M:S:speed     - Stop
  
  Author: Sonar System Project
  License: MIT
*/

// ===== PIN CONFIGURATION =====
// Ultrasonic Sensor
#define TRIG_PIN A3
#define ECHO_PIN A2

// Left Motor
#define LEFT_DIR1 2
#define LEFT_DIR2 4
#define LEFT_PWM 3

// Right Motor
#define RIGHT_DIR1 A0
#define RIGHT_DIR2 A1
#define RIGHT_PWM 5

// ===== SETTINGS =====
#define BAUD_RATE 250000      // Serial baud rate (match with Python)
#define MAX_DISTANCE 200      // Maximum detection distance (cm)
#define MOTOR_SPEED 255       // Motor speed for radar scanning
#define STEP_TIME_MS 60       // Rotation duration per step (ms)
#define TOTAL_STEPS 18        // Number of scan steps (18 = 10° intervals)
#define PULSE_TIMEOUT 12000   // Ultrasonic pulse timeout (microseconds)
#define MEASURE_SAMPLES 3     // Number of samples for averaging (stability)
#define SAMPLE_DELAY 5        // Delay between samples (ms)

// ===== VARIABLES =====
enum Mode { MODE_RADAR, MODE_CONTROL };
Mode currentMode = MODE_RADAR;
int motorSpeed = 200;         // Current motor speed for control mode
int currentPosition = 9;      // Current step position (9 = center = 90°)
bool initialized = false;     // Has robot been initialized to center?

// ===== SETUP =====
void setup() {
  Serial.begin(BAUD_RATE);
  
  // Motor pins
  pinMode(LEFT_DIR1, OUTPUT);
  pinMode(LEFT_DIR2, OUTPUT);
  pinMode(LEFT_PWM, OUTPUT);
  pinMode(RIGHT_DIR1, OUTPUT);
  pinMode(RIGHT_DIR2, OUTPUT);
  pinMode(RIGHT_PWM, OUTPUT);
  
  // Ultrasonic pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  stopMotors();
  Serial.println("READY");
}

// ===== MAIN LOOP =====
void loop() {
  processCommands();
  
  if (currentMode == MODE_RADAR) {
    doRadarSweep();
  } else {
    // In control mode, only look forward (90°)
    int dist = measureDistanceStable();
    Serial.print("90,");
    Serial.println(dist);
    delay(100);
  }
}

// ===== RADAR SWEEP (90° centered) =====
void doRadarSweep() {
  // Robot starts facing forward = 90° (center)
  // Sweep pattern: 90° -> 0° -> 180° -> 90°
  
  // Phase 1: Center to Right (90° -> 0°)
  for (int i = 9; i >= 0; i--) {
    int angle = (i * 180) / TOTAL_STEPS;
    int dist = measureDistanceStable();
    
    Serial.print(angle);
    Serial.print(",");
    Serial.println(dist);
    
    processCommands();
    if (currentMode != MODE_RADAR) return;
    
    if (i > 0) {
      stepRight();
    }
  }
  
  delay(100);
  
  // Phase 2: Right to Left (0° -> 180°)
  for (int i = 0; i <= TOTAL_STEPS; i++) {
    // Skip 0° as we already measured it
    if (i == 0) continue;
    
    int angle = (i * 180) / TOTAL_STEPS;
    
    stepLeft();
    
    int dist = measureDistanceStable();
    
    Serial.print(angle);
    Serial.print(",");
    Serial.println(dist);
    
    processCommands();
    if (currentMode != MODE_RADAR) return;
  }
  
  delay(100);
  
  // Phase 3: Left back to Center (180° -> 90°)
  for (int i = TOTAL_STEPS; i >= 9; i--) {
    // Skip 180° as we already measured it
    if (i == TOTAL_STEPS) continue;
    
    int angle = (i * 180) / TOTAL_STEPS;
    
    stepRight();
    
    int dist = measureDistanceStable();
    
    Serial.print(angle);
    Serial.print(",");
    Serial.println(dist);
    
    processCommands();
    if (currentMode != MODE_RADAR) return;
  }
  
  delay(200);
}

// ===== STEP FUNCTIONS (single step) =====
void stepLeft() {
  rotateLeft();
  delay(STEP_TIME_MS);
  stopMotors();
  delay(15);
}

void stepRight() {
  rotateRight();
  delay(STEP_TIME_MS);
  stopMotors();
  delay(15);
}

// ===== ULTRASONIC MEASUREMENT =====
int measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, PULSE_TIMEOUT);
  if (duration == 0) return MAX_DISTANCE;
  
  int dist = duration * 0.0343 / 2;
  return constrain(dist, 2, MAX_DISTANCE);
}

// Stable measurement with averaging (reduces noise)
int measureDistanceStable() {
  int readings[MEASURE_SAMPLES];
  int validCount = 0;
  long sum = 0;
  
  for (int i = 0; i < MEASURE_SAMPLES; i++) {
    int d = measureDistance();
    readings[i] = d;
    if (d < MAX_DISTANCE) {
      sum += d;
      validCount++;
    }
    if (i < MEASURE_SAMPLES - 1) {
      delay(SAMPLE_DELAY);
    }
  }
  
  // Return average of valid readings
  if (validCount > 0) {
    return sum / validCount;
  }
  return MAX_DISTANCE;
}

// ===== COMMAND PROCESSING =====
void processCommands() {
  if (!Serial.available()) return;
  
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  
  if (cmd == "MODE:RADAR") {
    currentMode = MODE_RADAR;
    stopMotors();
    resetToStart();
  } else if (cmd == "MODE:CONTROL") {
    currentMode = MODE_CONTROL;
    stopMotors();
  } else if (cmd.startsWith("M:")) {
    char dir = cmd.charAt(2);
    int colonPos = cmd.indexOf(':', 3);
    if (colonPos > 0) {
      motorSpeed = cmd.substring(colonPos + 1).toInt();
    }
    executeMove(dir);
  }
}

void executeMove(char dir) {
  switch(dir) {
    case 'F': moveForward(); break;
    case 'B': moveBackward(); break;
    case 'L': rotateLeftControl(); break;
    case 'R': rotateRightControl(); break;
    default: stopMotors(); break;
  }
}

// ===== MOTOR CONTROL =====
void rotateLeft() {
  digitalWrite(LEFT_DIR1, LOW);
  digitalWrite(LEFT_DIR2, HIGH);
  digitalWrite(RIGHT_DIR1, HIGH);
  digitalWrite(RIGHT_DIR2, LOW);
  analogWrite(LEFT_PWM, MOTOR_SPEED);
  analogWrite(RIGHT_PWM, MOTOR_SPEED);
}

void rotateRight() {
  digitalWrite(LEFT_DIR1, HIGH);
  digitalWrite(LEFT_DIR2, LOW);
  digitalWrite(RIGHT_DIR1, LOW);
  digitalWrite(RIGHT_DIR2, HIGH);
  analogWrite(LEFT_PWM, MOTOR_SPEED);
  analogWrite(RIGHT_PWM, MOTOR_SPEED);
}

void rotateLeftControl() {
  digitalWrite(LEFT_DIR1, LOW);
  digitalWrite(LEFT_DIR2, HIGH);
  digitalWrite(RIGHT_DIR1, HIGH);
  digitalWrite(RIGHT_DIR2, LOW);
  analogWrite(LEFT_PWM, motorSpeed);
  analogWrite(RIGHT_PWM, motorSpeed);
}

void rotateRightControl() {
  digitalWrite(LEFT_DIR1, HIGH);
  digitalWrite(LEFT_DIR2, LOW);
  digitalWrite(RIGHT_DIR1, LOW);
  digitalWrite(RIGHT_DIR2, HIGH);
  analogWrite(LEFT_PWM, motorSpeed);
  analogWrite(RIGHT_PWM, motorSpeed);
}

void moveForward() {
  digitalWrite(LEFT_DIR1, HIGH);
  digitalWrite(LEFT_DIR2, LOW);
  digitalWrite(RIGHT_DIR1, HIGH);
  digitalWrite(RIGHT_DIR2, LOW);
  analogWrite(LEFT_PWM, motorSpeed);
  analogWrite(RIGHT_PWM, motorSpeed);
}

void moveBackward() {
  digitalWrite(LEFT_DIR1, LOW);
  digitalWrite(LEFT_DIR2, HIGH);
  digitalWrite(RIGHT_DIR1, LOW);
  digitalWrite(RIGHT_DIR2, HIGH);
  analogWrite(LEFT_PWM, motorSpeed);
  analogWrite(RIGHT_PWM, motorSpeed);
}

void stopMotors() {
  analogWrite(LEFT_PWM, 0);
  analogWrite(RIGHT_PWM, 0);
}

void resetToStart() {
  // Return to center position (90° = forward)
  // This assumes we're at 0° and need to go to 90°
  for (int i = 0; i < 9; i++) {
    stepLeft();
  }
  delay(200);
}

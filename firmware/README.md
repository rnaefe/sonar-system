# Sonar System - Firmware

This folder contains the Arduino firmware for the Sonar System project.

## Files

- `sonar_robot/sonar_robot.ino` - Main firmware for HC-SR04 + motor control

## Hardware Requirements

- Arduino Uno, Nano, or compatible board
- HC-SR04 Ultrasonic Sensor
- L298N Motor Driver (or compatible)
- 2x DC Motors
- Robot chassis

## Pin Configuration

### Ultrasonic Sensor
| Pin | Arduino |
|-----|---------|
| VCC | 5V |
| GND | GND |
| TRIG | A3 |
| ECHO | A2 |

### Motor Driver
| Function | Arduino Pin |
|----------|-------------|
| Left Dir 1 | D2 |
| Left Dir 2 | D4 |
| Left PWM | D3 |
| Right Dir 1 | A0 |
| Right Dir 2 | A1 |
| Right PWM | D5 |

## Upload Instructions

1. Open `sonar_robot/sonar_robot.ino` in Arduino IDE
2. Select your board (Tools > Board > Arduino Uno)
3. Select your port (Tools > Port > COMX)
4. Click Upload

## Serial Protocol

**Baud Rate:** 250000

### Output Format
```
angle,distance
```
Example: `90,150` means 90° angle, 150cm distance

### Input Commands

| Command | Description |
|---------|-------------|
| `MODE:RADAR` | Switch to radar scanning mode |
| `MODE:CONTROL` | Switch to manual control mode |
| `M:F:speed` | Move forward (speed: 0-255) |
| `M:B:speed` | Move backward |
| `M:L:speed` | Turn left |
| `M:R:speed` | Turn right |
| `M:S:speed` | Stop |

## Customization

Edit these values in the code to match your hardware:

```cpp
#define STEP_TIME_MS 60       // Adjust for 180° rotation calibration
#define TOTAL_STEPS 18        // Number of scan steps
#define MAX_DISTANCE 200      // Maximum detection range
```

## Troubleshooting

### Robot doesn't rotate exactly 180°
Adjust `STEP_TIME_MS` value:
- Increase if rotating less than 180°
- Decrease if rotating more than 180°

### Sensor readings inaccurate
- Check wiring
- Increase `PULSE_TIMEOUT` for longer range
- Ensure clear path in front of sensor

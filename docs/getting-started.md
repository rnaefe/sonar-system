# Getting Started

This guide will help you set up and run the Sonar System.

## Prerequisites

- Python 3.8 or higher
- Arduino with HC-SR04 sensor
- USB cable for Arduino connection

## Installation

### 1. Get the Project

Download or clone the project and navigate to the folder:

```bash
cd sonar-system
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Serial Port

Edit `sonar_system/config/settings.py`:

```python
SERIAL = {
    "port": "COM5",       # Windows: COM3, COM4, etc.
                          # Linux: /dev/ttyUSB0, /dev/ttyACM0
                          # macOS: /dev/cu.usbserial-XXX
    "baud_rate": 250000,
}
```

### 5. Upload Arduino Firmware

1. Open Arduino IDE
2. Open `firmware/sonar_robot/sonar_robot.ino`
3. Select your board and port
4. Click Upload

### 6. Run the Application

```bash
python run.py
```

## First Run

When you start the application:

1. The Control Center window will open
2. If connected, you'll see "🟢 Connected!"
3. The radar will start scanning automatically
4. Use the dropdown to switch between radar types
5. Switch to Control Mode to move the robot

## Next Steps

- [Configuration Guide](configuration.md)
- [Radar Types Overview](radar-types.md)
- [Hardware Setup](hardware-setup.md)

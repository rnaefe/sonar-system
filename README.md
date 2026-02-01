# 🛸 Sonar System

A modular Python framework for HC-SR04 ultrasonic sensor visualization and robot control.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## ✨ Features

- **📡 Multiple Radar Views** - Switch between 4 different visualization styles
- **🎮 Robot Control** - Joystick and keyboard control for your robot
- **🔌 Serial Communication** - Real-time data from Arduino
- **🎨 Modern UI** - Dark theme with sci-fi aesthetics
- **📦 Modular Design** - Easy to extend with new radar types
- **⚙️ Configurable** - All settings in one place

## 🎯 Radar Types

| Radar | Description |
|-------|-------------|
| 📡 **Polar Radar** | Classic sonar-style polar plot with trail effect |
| 🌐 **3D LiDAR** | Real-time 3D point cloud with tunnel effect |
| 🤖 **Robot FOV** | First person view from robot's perspective |
| 🎯 **Object Detection** | Intelligent object detection with zone classification |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Arduino with HC-SR04 sensor and 2 motors
- USB connection to Arduino

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rnaefe/sonar-system.git
   cd sonar-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure serial port**
   
   Edit `sonar_system/config/settings.py`:
   ```python
   SERIAL = {
       "port": "COM5",  # Change to your port
       "baud_rate": 250000,
   }
   ```

4. **Upload Arduino firmware**
   
   Upload the firmware from `firmware/sonar_robot/sonar_robot.ino` to your Arduino.

5. **Run the application**
   ```bash
   python run.py
   ```

## 📁 Project Structure

```
sonar-system/
├── run.py                    # Entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
│
├── sonar_system/            # Main package
│   ├── __init__.py
│   ├── main.py              # Alternative entry point
│   ├── control_center.py    # Main application
│   │
│   ├── config/              # Configuration
│   │   ├── __init__.py
│   │   └── settings.py      # All settings
│   │
│   ├── core/                # Core components
│   │   ├── __init__.py
│   │   ├── serial_manager.py  # Serial communication
│   │   └── base_radar.py    # Base class for radars
│   │
│   ├── radars/              # Radar visualizations
│   │   ├── __init__.py
│   │   ├── polar_radar.py
│   │   ├── lidar_3d_radar.py
│   │   ├── robot_fov_radar.py
│   │   └── object_detection_radar.py
│   │
│   └── widgets/             # UI components
│       ├── __init__.py
│       ├── joystick.py
│       └── mini_radar.py
│
└── firmware/                # Arduino code
    └── sonar_robot/
        └── sonar_robot.ino
```

## 🎮 Controls

### Keyboard (Control Mode)
| Key | Action |
|-----|--------|
| W / ↑ | Move Forward |
| S / ↓ | Move Backward |
| A / ← | Turn Left |
| D / → | Turn Right |
| Space | Stop |

### Mouse
- **Joystick Widget** - Click and drag to control
- **3D View** - Rotate, zoom, and pan with mouse

## ⚙️ Configuration

All settings are in `sonar_system/config/settings.py`:

```python
# Serial connection
SERIAL = {
    "port": "COM5",
    "baud_rate": 250000,
}

# Sensor settings
SENSOR = {
    "max_distance": 200,
    "min_distance": 2,
}

# Object detection zones
DETECTION = {
    "danger_zone": 20,
    "warning_zone": 40,
}
```

## 🔧 Hardware Setup

### Components
- Arduino (Uno, Nano, or compatible)
- HC-SR04 Ultrasonic Sensor
- Motor Driver (L298N or similar)
- DC Motors (for robot movement)
- Robot chassis

### Wiring

| HC-SR04 | Arduino |
|---------|---------|
| VCC | 5V |
| GND | GND |
| TRIG | A3 |
| ECHO | A2 |

| Motor Driver | Arduino |
|--------------|---------|
| Left Motor | D2, D4, D3 (PWM) |
| Right Motor | A0, A1, D5 (PWM) |

## 🧩 Creating Custom Radars

You can easily add new radar types by extending `BaseRadar`:

```python
from sonar_system.core import BaseRadar

class MyCustomRadar(BaseRadar):
    NAME = "My Radar"
    DESCRIPTION = "My custom radar visualization"
    ICON = "🔮"
    
    def create_widget(self):
        # Create and return your widget
        pass
    
    def update_data(self, angle, distance):
        # Handle incoming data
        pass
    
    def clear(self):
        # Reset the visualization
        pass
```

Then register it in `sonar_system/radars/__init__.py`.

## 📦 Dependencies

- **PyQt5** - GUI framework
- **pyqtgraph** - Fast plotting
- **PyOpenGL** - 3D rendering
- **pyserial** - Serial communication
- **numpy** - Numerical operations
- **matplotlib** - Polar plots

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by DIY LiDAR and sonar projects
- Built with ❤️ using Python and PyQt5

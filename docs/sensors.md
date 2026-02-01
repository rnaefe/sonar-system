# Sensors

Scope: Sensor abstraction layer, available implementations, and extension guidance.

## Responsibility

Sensors produce angle-distance pairs. They manage their own connection lifecycle, threading, and error handling.

The visualization layer never imports concrete sensor classes. It receives a `BaseSensor` instance and subscribes to its signals.

## The Abstraction

`BaseSensor` defines the contract:

```python
class BaseSensor(QObject, ABC):
    data_received = pyqtSignal(int, float)  # angle, distance
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    def start(self) -> bool: ...
    def stop(self): ...
    def get_latest_reading(self) -> Optional[Tuple[int, float]]: ...
```

Any class implementing this interface can be used with the system.

## Implementations

### UltrasonicSensor

Connects to an Arduino running the sonar firmware via serial. Parses incoming lines in the format `angle,distance` and emits readings.

Features automatic port detection and reconnection. Supports sending motor commands for robot control.

Use this when you have real hardware connected.

### MockSensor

Generates synthetic readings with configurable noise characteristics. Simulates realistic scenarios: static walls, moving obstacles, varying noise levels.

The mock sensor exists because:

1. Development should not require hardware to be connected
2. Filtering behavior is easier to evaluate with controlled noise
3. Demonstrations work reliably without physical setup

Use this for development, testing, and demonstration.

## Scenario Presets

The mock sensor includes preset configurations:

| Preset | Behavior |
|--------|----------|
| `clean_wall` | Stable wall with minimal noise |
| `noisy_wall` | Wall with typical HC-SR04 jitter |
| `very_noisy` | Exaggerated noise for stress testing |
| `moving_obstacle` | Object moving through the sensor field |
| `realistic_room` | Complex room with multiple features |

These presets make it easy to evaluate filter effectiveness.

## Adding a New Sensor

To add support for a different sensor:

1. Create a class inheriting from `BaseSensor`
2. Implement `start()`, `stop()`, and `get_latest_reading()`
3. Emit `data_received` when new readings arrive
4. Emit `connection_changed` when connection state changes

The rest of the system requires no modification.

## Design Rationale

The sensor abstraction exists because the original implementation had visualization code checking `if isinstance(sensor, ArduinoSensor)`. This coupling made testing difficult and adding new sensors invasive.

By defining an abstract interface, sensors become interchangeable. The mock sensor enables offline development. Future sensors (infrared, LiDAR, network-based) require only implementing the interface.

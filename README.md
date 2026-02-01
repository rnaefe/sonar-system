# Sonar System

A modular sensor visualization framework with signal processing.

## Scope

This project explores three interconnected problems:

1. How to abstract hardware sensors so visualization code remains decoupled
2. How to filter noisy real-time data using composable signal processing
3. How to visualize distance measurements in multiple meaningful ways

The system works with HC-SR04 ultrasonic sensors but is designed to support any distance sensor that can provide angle-distance pairs.

## Why This Exists

Ultrasonic sensors produce noisy data. A stationary wall at 100cm might yield readings of 98, 103, 2, 101, 200, 99 over successive measurements. The spikes at 2cm and 200cm are sensor errors. The jitter of ±3cm is inherent noise.

Raw sensor data is rarely usable for decision-making. This project exists to demonstrate how abstraction and filtering address that problem, and to provide visualization tools that make the difference visible.

## Learning Goals

This project was built to develop competence in:

- Designing abstract interfaces that hide implementation details
- Implementing standard signal processing filters (moving average, median, Kalman)
- Building real-time PyQt5 applications with matplotlib integration
- Structuring Python projects for extensibility

These goals are stated explicitly because the codebase should be read with them in mind.

## Architecture

The system follows a pipeline architecture:

```
Sensor -> DataProcessor -> FilterChain -> Visualization
```

**Sensors** produce raw angle-distance pairs. Two implementations exist: `UltrasonicSensor` for real hardware, and `MockSensor` for testing without hardware. Both implement `BaseSensor`.

**DataProcessor** receives raw data, applies the filter chain, and emits both raw and filtered signals. This enables comparison visualization.

**FilterChain** composes multiple filters in sequence. The standard chain applies median filtering (to remove spikes) followed by smoothing (to reduce jitter).

**Visualization** displays the processed data. Multiple radar styles exist. The comparison radar shows raw and filtered data simultaneously.

## Project Structure

```
sonar_system/
    sensors/          # Sensor abstraction layer
    filters/          # Signal processing filters
    radars/           # Visualization implementations
    config/           # Configuration
    data_processor.py # Central data routing
    control_center_v2.py # Main application
```

Each directory has a specific responsibility. See the documentation in `/docs` for detailed explanations.

## What This Project Avoids

- **Over-engineering**: No dependency injection frameworks, no plugin systems, no configuration DSLs. The abstractions exist because they solve real problems, not because patterns are interesting.

- **Hardware lock-in**: The visualization layer does not import sensor implementations directly. Sensors are passed as abstract types.

- **Premature optimization**: Filters use simple Python data structures. Performance is adequate for 50Hz sensor data.

## Requirements

- Python 3.8+
- PyQt5
- matplotlib
- numpy
- pyserial (for hardware sensor)

## Usage

Run with simulated sensor (no hardware required):

```bash
python run.py
```

Run the legacy interface:

```bash
python run.py --legacy
```

Configuration is in `sonar_system/config/settings.py`.

## Documentation

- [Architecture](docs/architecture.md) — Design decisions and component boundaries
- [Sensors](docs/sensors.md) — Sensor abstraction and implementations
- [Filters](docs/filters.md) — Signal processing pipeline
- [Visualization](docs/visualization.md) — Radar types and comparison mode

## License

MIT

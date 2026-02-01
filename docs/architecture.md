# Architecture

Scope: System design decisions, component boundaries, and data flow.

## Design Intent

The architecture separates three concerns that often become entangled in sensor projects:

1. **Data acquisition** — Getting readings from hardware
2. **Data processing** — Cleaning and transforming readings
3. **Data presentation** — Displaying results to users

Each concern maps to a distinct layer. Layers communicate through defined interfaces, not concrete implementations.

## Component Boundaries

### Sensors

Sensors are responsible for producing angle-distance pairs. They handle connection management, threading, and hardware-specific protocols.

Sensors are not responsible for filtering, validation beyond basic range checks, or any display logic.

### DataProcessor

The DataProcessor receives raw readings from sensors and routes them through the filter chain. It emits two signals: raw data and filtered data.

The DataProcessor is not responsible for knowing which sensor is connected or how visualization works. It operates on the abstract `BaseSensor` interface.

### Filters

Filters transform individual readings. Each filter maintains per-angle state and processes values independently.

Filters are not responsible for data routing, connection state, or display. They are pure signal processing components.

### Visualization

Visualization components receive processed data and render it. They manage their own display state, animation, and user interaction.

Visualization is not responsible for data acquisition or processing. It consumes what the DataProcessor provides.

## Data Flow

```
Hardware/Simulation
        |
        v
   BaseSensor (emits raw readings)
        |
        v
   DataProcessor
        |
        +---> raw_data signal ---> ComparisonRadar (raw display)
        |
        v
   FilterChain
        |
        v
   filtered_data signal ---> Active Radar
                        ---> ComparisonRadar (filtered display)
```

The comparison radar subscribes to both signals, enabling side-by-side visualization.

## Why This Separation

**Testability**: The mock sensor allows testing the entire pipeline without hardware. Filters can be unit tested with synthetic data.

**Flexibility**: New sensors (infrared, LiDAR) require only implementing `BaseSensor`. New filters slot into the chain without touching visualization code.

**Clarity**: Each component has a single responsibility. When something breaks, the failure domain is obvious.

## What This Architecture Does Not Do

It does not support multiple simultaneous sensors. The DataProcessor binds to one sensor at a time.

It does not persist data. Readings exist only in memory during runtime.

It does not provide remote access. This is a local desktop application.

These limitations are intentional. The architecture solves the problems it was designed for and does not attempt to be a general-purpose sensor framework.

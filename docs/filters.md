# Filters

Scope: Signal processing pipeline, available filters, and composition patterns.

## Responsibility

Filters transform noisy sensor readings into stable values. They operate on individual angle-distance pairs, maintaining per-angle state to handle the radar's sweep pattern.

Filters do not know about sensors, connections, or visualization. They process values.

## The Problem Filters Solve

HC-SR04 sensors exhibit two types of noise:

**Jitter**: Readings fluctuate randomly around the true value. A wall at 100cm might read as 98, 102, 99, 101.

**Spikes**: Occasional readings are completely wrong. Values of 2cm or 200cm appear when the true distance is 100cm.

Different filter types address these problems differently.

## Available Filters

### MovingAverageFilter

Averages the last N readings for each angle.

Effective against jitter. The output follows trends smoothly. Introduces lag proportional to window size.

Does not handle spikes well. A single outlier affects the average for N readings.

### MedianFilter

Returns the median of the last N readings for each angle.

Effective against spikes. A single outlier does not affect the output if the window size is 3 or greater.

Less effective against jitter than moving average. Output can be slightly choppy.

### SimpleKalmanFilter

Maintains an estimate of the true value and adjusts based on incoming measurements. Balances trust in the current estimate against trust in new readings.

Provides smooth output with minimal lag when tuned correctly. Requires understanding of process noise and measurement noise parameters.

More complex to configure than the other filters.

## Composition

Filters can be chained:

```python
chain = FilterChain([
    MedianFilter(window_size=3),
    MovingAverageFilter(window_size=5)
])
```

The median filter removes spikes. The moving average smooths the remaining jitter. The combination handles both noise types.

## Presets

The `FilterPresets` class provides common configurations:

| Preset | Composition | Use Case |
|--------|-------------|----------|
| `none` | Empty chain | Raw data analysis |
| `light` | Moving average (3) | Minimal lag, some smoothing |
| `standard` | Median (3) + Moving average (3) | Balanced |
| `heavy` | Median (5) + Moving average (7) | Maximum smoothing, more lag |
| `kalman` | Median (3) + Kalman | Smooth tracking |

## Design Rationale

Filters are separate classes rather than functions because they maintain state. Each angle needs its own history buffer.

The chain pattern exists because no single filter handles all noise types well. Composition lets users tune the tradeoff between smoothing and responsiveness.

Filters process `float` values even though sensor readings are often integers. This preserves precision through the processing chain.

## Tradeoffs

All filtering introduces lag. The output reacts to changes slower than the raw input.

Heavy filtering makes the display stable but can mask real environmental changes. Light filtering preserves responsiveness but allows more noise through.

The comparison radar exists specifically to make these tradeoffs visible.

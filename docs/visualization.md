# Visualization

Scope: Radar display types, comparison mode, and display configuration.

## Responsibility

Visualization components render sensor data. They manage their own display state, handle user interaction, and update at the configured refresh rate.

Visualization does not process data. It receives already-processed readings from the DataProcessor.

## Available Radars

### Polar Radar

Classic sonar-style display. Plots distance on a semicircular grid with 0-180 degree sweep.

Shows a trail of recent readings, creating a persistence effect. The current sweep position is highlighted.

Useful for understanding the basic radar concept and seeing wall contours.

### 3D LiDAR

Renders readings as a 3D point cloud. Historical sweeps extend along the Z-axis, creating a tunnel effect.

Supports mouse interaction: rotate, zoom, pan. Uses OpenGL for rendering.

Useful for spatial understanding and demonstration purposes. More computationally intensive than 2D displays.

### Robot FOV

Top-down view centered on the robot's position. Shows the current scan as connected line segments.

Simpler than polar radar. Emphasizes the robot's immediate surroundings rather than historical data.

Useful when the focus is navigation rather than mapping.

### Object Detection

Processes readings to identify distinct objects and classifies distances into zones: danger, warning, safe.

Displays detected objects with bounding indicators and zone coloring.

Useful for obstacle avoidance applications and safety monitoring.

### Comparison Radar

Displays raw and filtered data simultaneously. Three modes:

- **Overlay**: Both datasets on the same plot, different colors
- **Side-by-side**: Two separate plots next to each other
- **Toggle**: Switch between raw and filtered views

Shows noise reduction statistics in real time.

This radar exists specifically to demonstrate why filtering matters. Seeing raw and filtered data together makes the value of the processing pipeline visible.

## Display Configuration

Settings in `config/settings.py`:

```python
DISPLAY = {
    "update_interval": 50,    # Milliseconds between refreshes
    "trail_length": 360,      # Points retained in trail displays
    "point_size": 4,          # Rendered point diameter
}
```

Lower update intervals increase smoothness but consume more CPU. Trail length affects memory usage and how much history is visible.

## Adding a New Radar

To create a new visualization:

1. Create a class inheriting from `BaseRadar`
2. Implement `create_widget()`, `update_data()`, and `clear()`
3. Set `NAME`, `DESCRIPTION`, and `ICON` class attributes
4. Register the class in `radars/__init__.py`

The radar will appear in the selection dropdown automatically.

## Design Rationale

Multiple radar types exist because different visualizations serve different purposes. The polar radar is intuitive for understanding sonar behavior. The 3D view is effective for demonstrations. The comparison radar is essential for evaluating filter performance.

Radars inherit from `BaseRadar` to ensure consistent interface. The control center can swap between radars without knowing their implementation details.

The comparison radar was added specifically because filtering improvements are difficult to appreciate without seeing the before/after difference. It makes an abstract concept concrete.

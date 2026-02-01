"""
Sonar System Configuration
All configurable settings in one place
"""

# ==================== SERIAL CONNECTION ====================
SERIAL = {
    "port": "COM5",           # Arduino serial port (COM5 on Windows, /dev/ttyUSB0 on Linux)
    "baud_rate": 250000,      # Baud rate (match with Arduino)
    "timeout": 0.1,           # Serial read timeout in seconds
}

# ==================== SENSOR SETTINGS ====================
SENSOR = {
    "max_distance": 200,      # Maximum detection distance in cm
    "min_distance": 2,        # Minimum valid distance in cm
    "angle_min": 0,           # Minimum scan angle
    "angle_max": 180,         # Maximum scan angle
}

# ==================== FILTERING SETTINGS ====================
FILTER = {
    "enabled": True,          # Enable filtering by default
    "default_preset": "standard",  # Options: "none", "light", "standard", "heavy", "kalman"
    
    # Moving Average settings
    "moving_average_window": 5,
    
    # Median Filter settings  
    "median_window": 5,
    
    # Kalman Filter settings
    "kalman_process_noise": 1.0,
    "kalman_measurement_noise": 10.0,
    
    # Spike detection threshold (cm)
    "spike_threshold": 50.0,
}

# ==================== MOCK SENSOR SETTINGS ====================
MOCK_SENSOR = {
    "scan_speed": 0.02,       # Time between readings (seconds)
    "noise_level": 5.0,       # Gaussian noise std dev (cm)
    "outlier_probability": 0.05,  # Chance of generating spike
    "scenario": "realistic",  # Options: "wall", "moving_object", "realistic"
}

# ==================== VISUALIZATION SETTINGS ====================
DISPLAY = {
    "update_interval": 50,    # Animation update interval in ms
    "trail_length": 360,      # Number of points to keep in trail
    "point_size": 4,          # Size of rendered points
    "window_width": 1200,     # Default window width
    "window_height": 700,     # Default window height
}

# ==================== 3D LIDAR SETTINGS ====================
LIDAR_3D = {
    "max_history_layers": 100,    # Number of Z-layers to keep
    "z_shift_amount": 5,          # How far to shift points back per sweep
}

# ==================== OBJECT DETECTION SETTINGS ====================
DETECTION = {
    "danger_zone": 20,            # Danger zone distance in cm
    "warning_zone": 40,           # Warning zone distance in cm
    "cluster_threshold": 15,      # Object clustering threshold in degrees
    "min_object_points": 2,       # Minimum points to form an object
}

# ==================== THEME / COLORS ====================
COLORS = {
    # Main colors
    "background": "#0a0a0a",
    "panel": "#1a1a1a",
    "accent": "#00ff88",
    "accent_dark": "#008844",
    "text": "#ffffff",
    "text_dim": "#888888",
    "grid": "#333333",
    
    # Status colors
    "danger": "#ff3366",
    "warning": "#ffaa00",
    "safe": "#00ff88",
    
    # Radar specific
    "beam": "#00ff00",
    "trail": "#00aa00",
    "obstacle": "#ff0000",
}

# ==================== MOTOR CONTROL (for control mode) ====================
MOTOR = {
    "default_speed": 150,     # Default motor speed (0-255)
    "max_speed": 255,         # Maximum motor speed
    "min_speed": 50,          # Minimum motor speed
}

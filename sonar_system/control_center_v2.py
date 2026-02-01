"""
Control Center v2 - Refactored main application with sensor abstraction and filtering.

This version demonstrates the clean architecture:
- Sensor abstraction (works with any BaseSensor implementation)
- Filtering pipeline (chainable, toggleable filters)
- Visual comparison mode (raw vs filtered data)
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFrame, QGridLayout, QGroupBox,
    QRadioButton, QButtonGroup, QComboBox, QStackedWidget, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .sensors import BaseSensor, UltrasonicSensor, MockSensor, ScenarioPresets
from .sensors.ultrasonic_sensor import get_available_ports
from .filters import FilterChain, FilterPresets
from .data_processor import DataProcessor
from .radars import AVAILABLE_RADARS, ComparisonRadar
from .widgets import JoystickWidget, MiniRadarWidget
from .config import SERIAL, DISPLAY, COLORS, MOTOR, FILTER, MOCK_SENSOR


class ControlCenterV2(QMainWindow):
    """
    Refactored Control Center with sensor abstraction and filtering.
    
    Key improvements:
    - Works with any sensor implementing BaseSensor
    - Integrated filtering pipeline
    - Comparison mode for raw vs filtered data
    - Mock sensor for testing without hardware
    """
    
    def __init__(self, sensor: BaseSensor = None):
        """
        Initialize the Control Center.
        
        Args:
            sensor: Optional sensor instance. If None, will create based on config.
        """
        super().__init__()
        self.setWindowTitle("🎮 Sonar System - Control Center v2")
        self.setMinimumSize(DISPLAY["window_width"], DISPLAY["window_height"])
        self._apply_styles()
        
        # Core components
        self.sensor = sensor
        self.data_processor = DataProcessor()
        self.filter_chain = self._create_filter_chain()
        self.data_processor.set_filter_chain(self.filter_chain)
        
        # State
        self.radars = {}
        self.current_radar = None
        self.comparison_radar = None
        self.use_mock_sensor = sensor is None
        
        # Setup UI
        self._setup_ui()
        
        # Initialize sensor
        self._init_sensor()
        
        # Keyboard support
        self.setFocusPolicy(Qt.StrongFocus)
    
    def _create_filter_chain(self) -> FilterChain:
        """Create filter chain from settings."""
        preset = FILTER.get("default_preset", "standard")
        presets = {
            "none": FilterPresets.none,
            "light": FilterPresets.light,
            "standard": FilterPresets.standard,
            "heavy": FilterPresets.heavy,
            "kalman": FilterPresets.kalman,
        }
        return presets.get(preset, FilterPresets.standard)()
    
    def _init_sensor(self):
        """Initialize the sensor based on configuration."""
        if self.sensor is None:
            # Default to mock sensor for safe testing
            self.sensor = MockSensor(
                scan_speed=MOCK_SENSOR["scan_speed"],
                noise_level=MOCK_SENSOR["noise_level"],
                outlier_probability=MOCK_SENSOR["outlier_probability"],
                scenario=MOCK_SENSOR["scenario"]
            )
            self.use_mock_sensor = True
        
        # Connect sensor to data processor
        self.data_processor.set_sensor(self.sensor)
        
        # Connect data processor to visualization
        self.data_processor.raw_data.connect(self._on_raw_data)
        self.data_processor.filtered_data.connect(self._on_filtered_data)
        self.data_processor.data_quality_warning.connect(self._on_quality_warning)
    
    def _apply_styles(self):
        """Apply application styles."""
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS['background']}; }}
            QLabel {{ color: {COLORS['text']}; font-family: 'Segoe UI'; }}
            QPushButton {{
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
                color: {COLORS['background']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_dark']};
            }}
            QGroupBox {{
                color: {COLORS['accent']};
                border: 2px solid {COLORS['accent']};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QComboBox {{
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['accent']};
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
            QCheckBox {{
                color: {COLORS['text']};
                font-size: 12px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QSlider::groove:horizontal {{
                background: {COLORS['panel']};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            QRadioButton {{
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
        """)
    
    def _setup_ui(self):
        """Setup the main UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # ===== LEFT PANEL =====
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)
        
        # ===== RIGHT PANEL (Radar View) =====
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        left_panel = QWidget()
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Sensor selector
        sensor_group = QGroupBox("🔌 SENSOR")
        sensor_layout = QVBoxLayout(sensor_group)
        
        self.sensor_selector = QComboBox()
        self.sensor_selector.addItem("🔧 Mock Sensor (Simulation)", "mock")
        self.sensor_selector.addItem("📡 HC-SR04 (Hardware)", "hardware")
        self.sensor_selector.currentIndexChanged.connect(self._on_sensor_type_changed)
        sensor_layout.addWidget(self.sensor_selector)
        
        # Port selector (for hardware)
        self.port_row = QWidget()
        port_layout = QHBoxLayout(self.port_row)
        port_layout.setContentsMargins(0, 5, 0, 0)
        
        self.port_selector = QComboBox()
        self._refresh_ports()
        port_layout.addWidget(self.port_selector, 1)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(35, 35)
        self.refresh_btn.clicked.connect(self._refresh_ports)
        port_layout.addWidget(self.refresh_btn)
        
        sensor_layout.addWidget(self.port_row)
        self.port_row.hide()  # Hidden by default (mock sensor)
        
        # Connect button
        self.connect_btn = QPushButton("▶️ Start Sensor")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        sensor_layout.addWidget(self.connect_btn)
        
        left_layout.addWidget(sensor_group)
        
        # Radar selector
        radar_group = QGroupBox("📡 RADAR TYPE")
        radar_layout = QVBoxLayout(radar_group)
        
        self.radar_selector = QComboBox()
        for radar_class in AVAILABLE_RADARS:
            self.radar_selector.addItem(
                f"{radar_class.ICON} {radar_class.NAME}",
                radar_class
            )
        self.radar_selector.currentIndexChanged.connect(self._on_radar_changed)
        radar_layout.addWidget(self.radar_selector)
        
        self.radar_desc = QLabel("")
        self.radar_desc.setWordWrap(True)
        self.radar_desc.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        radar_layout.addWidget(self.radar_desc)
        
        left_layout.addWidget(radar_group)
        
        # Filter controls
        filter_group = QGroupBox("🔬 FILTERING")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_enabled_cb = QCheckBox("Enable Filtering")
        self.filter_enabled_cb.setChecked(FILTER["enabled"])
        self.filter_enabled_cb.stateChanged.connect(self._on_filter_toggle)
        filter_layout.addWidget(self.filter_enabled_cb)
        
        preset_row = QHBoxLayout()
        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        preset_row.addWidget(preset_label)
        
        self.filter_preset = QComboBox()
        self.filter_preset.addItems(["None", "Light", "Standard", "Heavy", "Kalman"])
        self.filter_preset.setCurrentText(FILTER["default_preset"].capitalize())
        self.filter_preset.currentTextChanged.connect(self._on_filter_preset_changed)
        preset_row.addWidget(self.filter_preset, 1)
        
        filter_layout.addLayout(preset_row)
        
        self.filter_stats = QLabel("Noise reduction: --")
        self.filter_stats.setStyleSheet(f"color: {COLORS['accent']}; font-size: 10px;")
        filter_layout.addWidget(self.filter_stats)
        
        left_layout.addWidget(filter_group)
        
        # Mock sensor scenarios
        self.scenario_group = QGroupBox("🎭 SCENARIO")
        scenario_layout = QVBoxLayout(self.scenario_group)
        
        self.scenario_selector = QComboBox()
        self.scenario_selector.addItems(["Realistic Room", "Clean Wall", "Noisy Wall", "Very Noisy", "Moving Object"])
        self.scenario_selector.currentTextChanged.connect(self._on_scenario_changed)
        scenario_layout.addWidget(self.scenario_selector)
        
        left_layout.addWidget(self.scenario_group)
        
        # Mode selection
        mode_group = QGroupBox("🎯 MODE")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_buttons = QButtonGroup()
        self.radar_mode = QRadioButton("📡 Radar Mode (Scan Only)")
        self.control_mode = QRadioButton("🎮 Control Mode (Movement)")
        self.radar_mode.setChecked(True)
        
        self.mode_buttons.addButton(self.radar_mode, 0)
        self.mode_buttons.addButton(self.control_mode, 1)
        
        mode_layout.addWidget(self.radar_mode)
        mode_layout.addWidget(self.control_mode)
        left_layout.addWidget(mode_group)
        
        # Joystick
        joy_group = QGroupBox("🕹️ JOYSTICK")
        joy_layout = QVBoxLayout(joy_group)
        
        self.joystick = JoystickWidget()
        self.joystick.moved.connect(self._on_joystick_move)
        joy_layout.addWidget(self.joystick, alignment=Qt.AlignCenter)
        
        self.joy_label = QLabel("X: 0.00  Y: 0.00")
        self.joy_label.setAlignment(Qt.AlignCenter)
        self.joy_label.setStyleSheet(f"color: {COLORS['accent']}; font-size: 11px;")
        joy_layout.addWidget(self.joy_label)
        
        left_layout.addWidget(joy_group)
        
        # Connection status
        self.status_label = QLabel("🟡 Ready - Select sensor and start")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['warning']};
            font-size: 11px;
            padding: 8px;
            background: {COLORS['panel']};
            border-radius: 5px;
        """)
        left_layout.addWidget(self.status_label)
        
        left_layout.addStretch()
        
        return left_panel
    
    def _create_right_panel(self) -> QWidget:
        """Create the right radar view panel."""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        # Radar title
        self.radar_title = QLabel("📡 RADAR VIEW")
        self.radar_title.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 20px;
            font-weight: bold;
            padding: 5px;
        """)
        self.radar_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.radar_title)
        
        # Stacked widget for radar views
        self.radar_stack = QStackedWidget()
        right_layout.addWidget(self.radar_stack, 1)
        
        # Initialize all radars
        for radar_class in AVAILABLE_RADARS:
            radar = radar_class()
            widget = radar.create_widget()
            self.radar_stack.addWidget(widget)
            self.radars[radar_class.NAME] = radar
            
            # Keep reference to comparison radar
            if isinstance(radar, ComparisonRadar):
                self.comparison_radar = radar
        
        # Set initial radar
        if AVAILABLE_RADARS:
            self._on_radar_changed(0)
        
        # Bottom info panel
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Mini radar
        mini_group = QGroupBox("🗺️ MAP")
        mini_layout = QVBoxLayout(mini_group)
        self.mini_radar = MiniRadarWidget()
        mini_layout.addWidget(self.mini_radar, alignment=Qt.AlignCenter)
        bottom_layout.addWidget(mini_group)
        
        # Info display
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            background: {COLORS['panel']};
            border-radius: 10px;
            padding: 10px;
        """)
        info_layout = QVBoxLayout(info_frame)
        
        self.angle_label = QLabel("📐 Angle: 0°")
        self.dist_label = QLabel("📏 Raw: --cm | Filtered: --cm")
        self.min_dist_label = QLabel("⚠️ Closest: --cm")
        
        for label in [self.angle_label, self.dist_label, self.min_dist_label]:
            label.setStyleSheet(f"""
                color: {COLORS['accent']};
                font-size: 14px;
                font-family: 'Consolas';
                padding: 3px;
            """)
            info_layout.addWidget(label)
        
        bottom_layout.addWidget(info_frame)
        right_layout.addWidget(bottom_panel)
        
        return right_panel
    
    def _refresh_ports(self):
        """Refresh available serial ports."""
        self.port_selector.clear()
        self.port_selector.addItem("🔍 Auto-detect", None)
        
        ports = get_available_ports()
        for port, desc in ports:
            display = f"{port} - {desc[:30]}" if len(desc) > 30 else f"{port} - {desc}"
            self.port_selector.addItem(display, port)
    
    def _on_sensor_type_changed(self, index: int):
        """Handle sensor type change."""
        sensor_type = self.sensor_selector.itemData(index)
        if sensor_type == "mock":
            self.port_row.hide()
            self.scenario_group.show()
        else:
            self.port_row.show()
            self.scenario_group.hide()
    
    def _on_scenario_changed(self, scenario_name: str):
        """Change mock sensor scenario."""
        if not self.use_mock_sensor or not self.sensor:
            return
        
        # Stop current sensor
        was_running = self.sensor.is_running
        if was_running:
            self.sensor.stop()
        
        # Create new sensor with selected scenario
        scenarios = {
            "Realistic Room": ScenarioPresets.realistic_room,
            "Clean Wall": ScenarioPresets.clean_wall,
            "Noisy Wall": ScenarioPresets.noisy_wall,
            "Very Noisy": ScenarioPresets.very_noisy,
            "Moving Object": ScenarioPresets.moving_obstacle,
        }
        
        factory = scenarios.get(scenario_name, ScenarioPresets.realistic_room)
        self.sensor = factory()
        self.data_processor.set_sensor(self.sensor)
        self.data_processor.reset()
        
        # Clear radars
        for radar in self.radars.values():
            radar.clear()
        
        # Restart if was running
        if was_running:
            self.sensor.start()
    
    def _on_connect_clicked(self):
        """Handle connect/disconnect button."""
        if self.sensor and self.sensor.is_running:
            # Stop
            self.sensor.stop()
            self.connect_btn.setText("▶️ Start Sensor")
            self.status_label.setText("🔴 Stopped")
            self.status_label.setStyleSheet(f"""
                color: {COLORS['danger']};
                font-size: 11px;
                padding: 8px;
                background: {COLORS['panel']};
                border-radius: 5px;
            """)
        else:
            # Create sensor if needed
            sensor_type = self.sensor_selector.currentData()
            
            if sensor_type == "hardware":
                port = self.port_selector.currentData()
                self.sensor = UltrasonicSensor(
                    port=port,
                    baud_rate=SERIAL["baud_rate"],
                    timeout=SERIAL["timeout"]
                )
                self.use_mock_sensor = False
            else:
                # Use current mock sensor or create new
                if not isinstance(self.sensor, MockSensor):
                    self._on_scenario_changed(self.scenario_selector.currentText())
                self.use_mock_sensor = True
            
            # Connect and start
            self.data_processor.set_sensor(self.sensor)
            self.sensor.start()
            
            self.connect_btn.setText("⏹️ Stop Sensor")
            sensor_name = "Mock" if self.use_mock_sensor else "HC-SR04"
            self.status_label.setText(f"🟢 Running ({sensor_name})")
            self.status_label.setStyleSheet(f"""
                color: {COLORS['accent']};
                font-size: 11px;
                padding: 8px;
                background: {COLORS['panel']};
                border-radius: 5px;
            """)
    
    def _on_radar_changed(self, index: int):
        """Handle radar type change."""
        radar_class = self.radar_selector.itemData(index)
        if radar_class:
            self.current_radar = self.radars.get(radar_class.NAME)
            self.radar_stack.setCurrentIndex(index)
            self.radar_title.setText(f"{radar_class.ICON} {radar_class.NAME.upper()}")
            self.radar_desc.setText(radar_class.DESCRIPTION)
    
    def _on_filter_toggle(self, state: int):
        """Toggle filtering on/off."""
        enabled = state == Qt.Checked
        self.data_processor.enable_filtering(enabled)
        self.filter_preset.setEnabled(enabled)
    
    def _on_filter_preset_changed(self, preset_name: str):
        """Change filter preset."""
        presets = {
            "None": FilterPresets.none,
            "Light": FilterPresets.light,
            "Standard": FilterPresets.standard,
            "Heavy": FilterPresets.heavy,
            "Kalman": FilterPresets.kalman,
        }
        factory = presets.get(preset_name, FilterPresets.standard)
        self.filter_chain = factory()
        self.data_processor.set_filter_chain(self.filter_chain)
    
    def _on_raw_data(self, angle: int, distance: float):
        """Handle raw data from sensor."""
        # Update mini radar with raw data
        self.mini_radar.update_data(angle, int(distance))
        
        # Update angle display
        self.angle_label.setText(f"📐 Angle: {angle}°")
        
        # If using comparison radar, send raw data
        if self.comparison_radar:
            self.comparison_radar.update_data(angle, int(distance))
    
    def _on_filtered_data(self, angle: int, distance: float):
        """Handle filtered data."""
        # Update main radar (non-comparison)
        if self.current_radar and not isinstance(self.current_radar, ComparisonRadar):
            self.current_radar.update_data(angle, int(distance))
        
        # Update comparison radar with filtered data
        if self.comparison_radar:
            self.comparison_radar.update_filtered_data(angle, distance)
            
            # Update stats
            stats = self.data_processor.get_stats()
            if stats["readings_processed"] > 0:
                avg_reduction = stats["noise_filtered"] / stats["readings_processed"]
                self.comparison_radar.update_stats(avg_reduction, stats["spikes_detected"])
                self.filter_stats.setText(f"Noise reduction: {avg_reduction:.1f}cm avg")
        
        # Update distance display
        raw_data = self.data_processor.get_raw_data()
        raw_dist = raw_data.get(angle, distance)
        self.dist_label.setText(f"📏 Raw: {raw_dist:.1f}cm | Filtered: {distance:.1f}cm")
    
    def _on_quality_warning(self, message: str):
        """Handle data quality warnings."""
        print(f"⚠️ Quality: {message}")
    
    def _on_joystick_move(self, x: float, y: float):
        """Handle joystick movement."""
        self.joy_label.setText(f"X: {x:.2f}  Y: {y:.2f}")
        
        if self.control_mode.isChecked() and not self.use_mock_sensor:
            if abs(x) < 0.2 and abs(y) < 0.2:
                self._send_move('S')
            elif y > 0.5:
                self._send_move('F')
            elif y < -0.5:
                self._send_move('B')
            elif x < -0.5:
                self._send_move('L')
            elif x > 0.5:
                self._send_move('R')
    
    def _send_move(self, direction: str):
        """Send movement command to hardware sensor."""
        if isinstance(self.sensor, UltrasonicSensor):
            self.sensor.send_command(f"M:{direction}:150")
    
    def keyPressEvent(self, event):
        """Handle keyboard input."""
        if self.control_mode.isChecked() and not self.use_mock_sensor:
            key = event.key()
            if key in [Qt.Key_W, Qt.Key_Up]:
                self._send_move('F')
            elif key in [Qt.Key_S, Qt.Key_Down]:
                self._send_move('B')
            elif key in [Qt.Key_A, Qt.Key_Left]:
                self._send_move('L')
            elif key in [Qt.Key_D, Qt.Key_Right]:
                self._send_move('R')
            elif key == Qt.Key_Space:
                self._send_move('S')
    
    def keyReleaseEvent(self, event):
        """Handle keyboard release."""
        if self.control_mode.isChecked() and not self.use_mock_sensor:
            key = event.key()
            if key in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D,
                      Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:
                self._send_move('S')
    
    def closeEvent(self, event):
        """Handle window close."""
        if self.sensor:
            self.sensor.stop()
        event.accept()


def run():
    """Run the Control Center v2 application."""
    print("=" * 50)
    print("🎮 SONAR SYSTEM - CONTROL CENTER v2.0")
    print("=" * 50)
    print("Features:")
    print("  - Sensor abstraction (Mock / Hardware)")
    print("  - Filtering pipeline (None/Light/Standard/Heavy/Kalman)")
    print("  - Visual comparison mode (Raw vs Filtered)")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Ctrl+C support
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    
    window = ControlCenterV2()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

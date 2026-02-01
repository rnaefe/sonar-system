"""
Control Center - Main application with switchable radar views
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFrame, QGridLayout, QGroupBox,
    QRadioButton, QButtonGroup, QComboBox, QStackedWidget, QSplitter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .core import SerialManager, get_available_ports, find_arduino_port
from .radars import AVAILABLE_RADARS
from .widgets import JoystickWidget, MiniRadarWidget
from .config import SERIAL, DISPLAY, COLORS, MOTOR


class ControlCenter(QMainWindow):
    """
    Main Control Center application.
    
    Features:
    - Switchable radar visualizations
    - Robot control mode with joystick
    - Real-time serial communication
    - Mini radar map
    - Status display
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 Sonar System - Control Center")
        self.setMinimumSize(DISPLAY["window_width"], DISPLAY["window_height"])
        self._apply_styles()
        
        # Initialize radars
        self.radars = {}
        self.current_radar = None
        self.serial = None
        
        # Setup UI
        self._setup_ui()
        
        # Setup serial connection (auto-scan enabled)
        self._init_serial()
        
        # Keyboard support
        self.setFocusPolicy(Qt.StrongFocus)
    
    def _init_serial(self):
        """Initialize serial connection with auto-reconnect"""
        # Get selected port or use auto-scan
        port = None
        if hasattr(self, 'port_selector') and self.port_selector.currentData():
            port = self.port_selector.currentData()
        else:
            port = SERIAL.get("port")
        
        self.serial = SerialManager(
            port, 
            SERIAL["baud_rate"], 
            SERIAL["timeout"]
        )
        self.serial.data_received.connect(self._on_data_received)
        self.serial.connection_changed.connect(self._on_connection_changed)
        self.serial.error_occurred.connect(self._on_serial_error)
        self.serial.reconnect_attempt.connect(self._on_reconnect_attempt)
        self.serial.port_found.connect(self._on_port_found)
        self.serial.start()
        
        # Keyboard support
        self.setFocusPolicy(Qt.StrongFocus)
    
    def _apply_styles(self):
        """Apply application styles"""
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
        """Setup the main UI"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # ===== LEFT PANEL =====
        left_panel = QWidget()
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
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
        
        # Connection / Port selector
        conn_group = QGroupBox("🔌 CONNECTION")
        conn_layout = QVBoxLayout(conn_group)
        
        # Port selector
        port_row = QHBoxLayout()
        self.port_selector = QComboBox()
        self.port_selector.setMinimumWidth(150)
        self._refresh_ports()
        port_row.addWidget(self.port_selector, 1)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(35, 35)
        self.refresh_btn.clicked.connect(self._refresh_ports)
        port_row.addWidget(self.refresh_btn)
        
        conn_layout.addLayout(port_row)
        
        # Connect button
        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        conn_layout.addWidget(self.connect_btn)
        
        left_layout.addWidget(conn_group)
        
        # Mode selection
        mode_group = QGroupBox("🎯 MODE")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_buttons = QButtonGroup()
        self.radar_mode = QRadioButton("📡 Radar Mode (Scan Only)")
        self.control_mode = QRadioButton("🎮 Control Mode (Movement)")
        self.radar_mode.setChecked(True)
        
        self.mode_buttons.addButton(self.radar_mode, 0)
        self.mode_buttons.addButton(self.control_mode, 1)
        
        self.radar_mode.toggled.connect(self._on_mode_changed)
        
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
        
        # Speed control
        speed_group = QGroupBox("⚡ SPEED")
        speed_layout = QVBoxLayout(speed_group)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(MOTOR["min_speed"], MOTOR["max_speed"])
        self.speed_slider.setValue(MOTOR["default_speed"])
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel(f"Speed: {MOTOR['default_speed']}")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(f"Speed: {v}")
        )
        speed_layout.addWidget(self.speed_label)
        
        left_layout.addWidget(speed_group)
        
        # Quick control buttons
        btn_group = QGroupBox("🎛️ QUICK CONTROL")
        btn_layout = QGridLayout(btn_group)
        
        self.btn_forward = QPushButton("⬆️")
        self.btn_backward = QPushButton("⬇️")
        self.btn_left = QPushButton("⬅️")
        self.btn_right = QPushButton("➡️")
        self.btn_stop = QPushButton("🛑")
        
        for btn in [self.btn_forward, self.btn_backward, self.btn_left, 
                    self.btn_right, self.btn_stop]:
            btn.setFixedSize(50, 50)
        
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                border-color: {COLORS['danger']};
            }}
        """)
        
        btn_layout.addWidget(self.btn_forward, 0, 1)
        btn_layout.addWidget(self.btn_left, 1, 0)
        btn_layout.addWidget(self.btn_stop, 1, 1)
        btn_layout.addWidget(self.btn_right, 1, 2)
        btn_layout.addWidget(self.btn_backward, 2, 1)
        
        # Button signals
        self.btn_forward.pressed.connect(lambda: self._send_move('F'))
        self.btn_backward.pressed.connect(lambda: self._send_move('B'))
        self.btn_left.pressed.connect(lambda: self._send_move('L'))
        self.btn_right.pressed.connect(lambda: self._send_move('R'))
        self.btn_stop.clicked.connect(lambda: self._send_move('S'))
        
        self.btn_forward.released.connect(lambda: self._send_move('S'))
        self.btn_backward.released.connect(lambda: self._send_move('S'))
        self.btn_left.released.connect(lambda: self._send_move('S'))
        self.btn_right.released.connect(lambda: self._send_move('S'))
        
        left_layout.addWidget(btn_group)
        
        # Connection status
        self.status_label = QLabel("🔴 Waiting for connection...")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['warning']};
            font-size: 11px;
            padding: 8px;
            background: {COLORS['panel']};
            border-radius: 5px;
        """)
        left_layout.addWidget(self.status_label)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # ===== RIGHT PANEL =====
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
        self.dist_label = QLabel("📏 Distance: --cm")
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
        
        main_layout.addWidget(right_panel, 1)
        
        # Min distance tracking
        self.min_distance = 9999
    
    def _on_radar_changed(self, index: int):
        """Handle radar type change"""
        radar_class = self.radar_selector.itemData(index)
        if radar_class:
            self.current_radar = self.radars.get(radar_class.NAME)
            self.radar_stack.setCurrentIndex(index)
            self.radar_title.setText(f"{radar_class.ICON} {radar_class.NAME.upper()}")
            self.radar_desc.setText(radar_class.DESCRIPTION)
    
    def _on_mode_changed(self):
        """Handle mode change"""
        if self.radar_mode.isChecked():
            self.serial.send_command("MODE:RADAR")
            self.status_label.setText("🟢 Radar Mode")
        else:
            self.serial.send_command("MODE:CONTROL")
            self.status_label.setText("🟢 Control Mode")
    
    def _on_data_received(self, angle: int, distance: int):
        """Handle incoming data"""
        # Update current radar
        if self.current_radar:
            self.current_radar.update_data(angle, distance)
        
        # Update mini radar
        self.mini_radar.update_data(angle, distance)
        
        # Track minimum distance
        if distance < self.min_distance:
            self.min_distance = distance
        
        # Update labels
        self.angle_label.setText(f"📐 Angle: {angle}°")
        self.dist_label.setText(f"📏 Distance: {distance}cm")
        self.min_dist_label.setText(f"⚠️ Closest: {self.min_distance}cm")
    
    def _on_connection_changed(self, connected: bool):
        """Handle connection status change"""
        if connected:
            self.status_label.setText("🟢 Connected!")
            self.status_label.setStyleSheet(f"""
                color: {COLORS['accent']};
                font-size: 11px;
                padding: 8px;
                background: {COLORS['panel']};
                border-radius: 5px;
            """)
            self.connect_btn.setText("🔌 Disconnect")
            # Send initial mode
            QTimer.singleShot(500, lambda: self.serial.send_command("MODE:RADAR"))
        else:
            self.status_label.setText("🔴 Disconnected")
            self.status_label.setStyleSheet(f"""
                color: {COLORS['danger']};
                font-size: 11px;
                padding: 8px;
                background: {COLORS['panel']};
                border-radius: 5px;
            """)
            self.connect_btn.setText("🔌 Connect")
    
    def _on_serial_error(self, message: str):
        """Handle serial errors"""
        print(f"Serial Error: {message}")
    
    def _on_reconnect_attempt(self, attempt: int):
        """Handle reconnect attempts"""
        self.status_label.setText(f"🔄 Reconnecting... ({attempt})")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['warning']};
            font-size: 11px;
            padding: 8px;
            background: {COLORS['panel']};
            border-radius: 5px;
        """)
    
    def _on_port_found(self, port: str):
        """Handle auto-detected port"""
        print(f"Auto-detected port: {port}")
        # Update port selector
        for i in range(self.port_selector.count()):
            if self.port_selector.itemData(i) == port:
                self.port_selector.setCurrentIndex(i)
                break
    
    def _refresh_ports(self):
        """Refresh available serial ports"""
        self.port_selector.clear()
        self.port_selector.addItem("🔍 Auto-detect", None)
        
        ports = get_available_ports()
        for port, desc in ports:
            display = f"{port} - {desc[:30]}" if len(desc) > 30 else f"{port} - {desc}"
            self.port_selector.addItem(display, port)
        
        # Try to select configured port
        for i in range(self.port_selector.count()):
            if self.port_selector.itemData(i) == SERIAL.get("port"):
                self.port_selector.setCurrentIndex(i)
                break
    
    def _on_connect_clicked(self):
        """Handle connect/disconnect button"""
        if self.serial and self.serial.is_connected():
            # Disconnect
            self.serial.stop()
            self.serial.wait()
            self.status_label.setText("🔴 Disconnected")
            self.connect_btn.setText("🔌 Connect")
        else:
            # Connect with selected port
            if self.serial:
                self.serial.stop()
                self.serial.wait()
            
            port = self.port_selector.currentData()  # None = auto-detect
            self.serial = SerialManager(
                port,
                SERIAL["baud_rate"],
                SERIAL["timeout"]
            )
            self.serial.data_received.connect(self._on_data_received)
            self.serial.connection_changed.connect(self._on_connection_changed)
            self.serial.error_occurred.connect(self._on_serial_error)
            self.serial.reconnect_attempt.connect(self._on_reconnect_attempt)
            self.serial.port_found.connect(self._on_port_found)
            self.serial.start()
            
            self.status_label.setText("🔄 Connecting...")
            self.status_label.setStyleSheet(f"""
                color: {COLORS['warning']};
                font-size: 11px;
                padding: 8px;
                background: {COLORS['panel']};
                border-radius: 5px;
            """)
    
    def _on_joystick_move(self, x: float, y: float):
        """Handle joystick movement"""
        self.joy_label.setText(f"X: {x:.2f}  Y: {y:.2f}")
        
        if self.control_mode.isChecked():
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
        """Send movement command"""
        if self.control_mode.isChecked():
            speed = self.speed_slider.value()
            self.serial.send_command(f"M:{direction}:{speed}")
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if self.control_mode.isChecked():
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
        """Handle keyboard release"""
        if self.control_mode.isChecked():
            key = event.key()
            if key in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D,
                      Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:
                self._send_move('S')
    
    def closeEvent(self, event):
        """Handle window close"""
        self.serial.stop()
        self.serial.wait()
        event.accept()


def run():
    """Run the Control Center application"""
    print("=" * 50)
    print("🎮 SONAR SYSTEM - CONTROL CENTER")
    print("=" * 50)
    print(f"Port: {SERIAL['port']} @ {SERIAL['baud_rate']}")
    print("=" * 50)
    print("\n⌨️ Keyboard Controls (Control Mode):")
    print("   W/↑ : Forward")
    print("   S/↓ : Backward")
    print("   A/← : Left")
    print("   D/→ : Right")
    print("   Space: Stop")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Ctrl+C support
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    
    window = ControlCenter()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

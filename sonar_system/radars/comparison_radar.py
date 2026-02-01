"""
Comparison Radar Widget - Side-by-side or overlay comparison of raw vs filtered data.

This widget demonstrates the effectiveness of the filtering pipeline
by showing raw sensor data alongside the filtered output.
"""

import math
import numpy as np
from collections import deque
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QCheckBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..core.base_radar import BaseRadar
from ..config import SENSOR, DISPLAY, COLORS


class ComparisonRadar(BaseRadar):
    """
    Comparison visualization showing raw vs filtered data.
    
    Modes:
    - Side-by-side: Two polar plots next to each other
    - Overlay: Single plot with both datasets overlaid
    - Toggle: Switch between raw and filtered views
    """
    
    NAME = "Comparison Radar"
    DESCRIPTION = "Visual comparison of raw vs filtered sensor data"
    ICON = "⚖️"
    
    def __init__(self):
        super().__init__()
        self.raw_data = {}
        self.filtered_data = {}
        self.raw_trail = deque(maxlen=DISPLAY["trail_length"])
        self.filtered_trail = deque(maxlen=DISPLAY["trail_length"])
        self.current_angle = 0
        self.mode = "overlay"  # "side-by-side", "overlay", "toggle"
        self.show_raw = True
        self.show_filtered = True
        
        # Matplotlib elements
        self.fig = None
        self.ax_raw = None
        self.ax_filtered = None
        self.ax_overlay = None
        self.canvas = None
        
        # Statistics
        self.noise_stats = {"reduction": 0.0, "spikes": 0}
    
    def create_widget(self) -> QWidget:
        """Create the comparison radar widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Control bar
        control_bar = self._create_control_bar()
        layout.addWidget(control_bar)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 5), facecolor=COLORS["background"])
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        # Statistics bar
        self.stats_label = QLabel("Noise Reduction: -- | Spikes Detected: --")
        self.stats_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 12px;
            font-family: 'Consolas';
            padding: 5px;
            background: {COLORS['panel']};
            border-radius: 5px;
        """)
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        
        # Initialize plot for overlay mode
        self._setup_overlay_plot()
        
        self.widget = widget
        return widget
    
    def _create_control_bar(self) -> QFrame:
        """Create the control bar for comparison options."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['panel']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Mode selector
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold;")
        layout.addWidget(mode_label)
        
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Overlay", "Side-by-Side", "Toggle"])
        self.mode_selector.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['background']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }}
        """)
        self.mode_selector.currentTextChanged.connect(self._on_mode_changed)
        layout.addWidget(self.mode_selector)
        
        layout.addSpacing(20)
        
        # Show/hide checkboxes
        self.show_raw_cb = QCheckBox("Show Raw")
        self.show_raw_cb.setChecked(True)
        self.show_raw_cb.setStyleSheet(f"color: #ff6b6b;")
        self.show_raw_cb.stateChanged.connect(self._on_visibility_changed)
        layout.addWidget(self.show_raw_cb)
        
        self.show_filtered_cb = QCheckBox("Show Filtered")
        self.show_filtered_cb.setChecked(True)
        self.show_filtered_cb.setStyleSheet(f"color: {COLORS['accent']};")
        self.show_filtered_cb.stateChanged.connect(self._on_visibility_changed)
        layout.addWidget(self.show_filtered_cb)
        
        layout.addStretch()
        
        # Legend
        legend = QLabel("● Raw (Red)  ● Filtered (Green)")
        legend.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        layout.addWidget(legend)
        
        return frame
    
    def _on_mode_changed(self, mode: str):
        """Handle display mode change."""
        mode_map = {"Overlay": "overlay", "Side-by-Side": "side-by-side", "Toggle": "toggle"}
        self.mode = mode_map.get(mode, "overlay")
        self._refresh_layout()
    
    def _on_visibility_changed(self):
        """Handle visibility toggle."""
        self.show_raw = self.show_raw_cb.isChecked()
        self.show_filtered = self.show_filtered_cb.isChecked()
        self._refresh_display()
    
    def _refresh_layout(self):
        """Reconfigure plot layout based on mode."""
        self.fig.clear()
        
        if self.mode == "side-by-side":
            self._setup_sidebyside_plot()
        elif self.mode == "toggle":
            self._setup_toggle_plot()
        else:
            self._setup_overlay_plot()
        
        self._refresh_display()
    
    def _setup_overlay_plot(self):
        """Setup single polar plot for overlay mode."""
        self.ax_overlay = self.fig.add_subplot(111, projection='polar', 
                                                facecolor=COLORS["background"])
        self._configure_polar_axis(self.ax_overlay, "⚖️ RAW vs FILTERED")
        
        # Create plot elements for both data streams
        self.raw_scatter = self.ax_overlay.scatter([], [], c='#ff6b6b', s=15, 
                                                    alpha=0.6, label='Raw')
        self.filtered_scatter = self.ax_overlay.scatter([], [], c=COLORS['accent'], 
                                                         s=20, alpha=0.8, label='Filtered')
        self.ax_overlay.legend(loc='upper right', fontsize=8, 
                               facecolor=COLORS['panel'], labelcolor=COLORS['text'])
    
    def _setup_sidebyside_plot(self):
        """Setup two polar plots side by side."""
        self.ax_raw = self.fig.add_subplot(121, projection='polar', 
                                            facecolor=COLORS["background"])
        self.ax_filtered = self.fig.add_subplot(122, projection='polar', 
                                                 facecolor=COLORS["background"])
        
        self._configure_polar_axis(self.ax_raw, "📊 RAW DATA")
        self._configure_polar_axis(self.ax_filtered, "✨ FILTERED DATA")
        
        self.raw_scatter = self.ax_raw.scatter([], [], c='#ff6b6b', s=20, alpha=0.8)
        self.filtered_scatter = self.ax_filtered.scatter([], [], 
                                                          c=COLORS['accent'], s=20, alpha=0.8)
    
    def _setup_toggle_plot(self):
        """Setup single plot for toggle mode (same as overlay visually)."""
        self._setup_overlay_plot()
    
    def _configure_polar_axis(self, ax, title: str):
        """Configure a polar axis with standard radar styling."""
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_theta_zero_location('S')
        ax.set_theta_direction(-1)
        ax.set_rlim(0, SENSOR["max_distance"])
        
        ax.grid(True, color=COLORS["accent"], alpha=0.3, linewidth=0.5)
        ax.tick_params(colors=COLORS["accent"], labelsize=8)
        
        ax.set_rticks([50, 100, 150, 200])
        ax.set_yticklabels(['50', '100', '150', '200cm'], 
                           color=COLORS["accent"], fontsize=7)
        
        ax.set_xticks([math.radians(a) for a in [0, 45, 90, 135, 180]])
        ax.set_xticklabels(['0°', '45°', '90°', '135°', '180°'], 
                           color=COLORS["accent"], fontsize=8)
        
        ax.spines['polar'].set_color(COLORS["accent"])
        ax.spines['polar'].set_linewidth(1.5)
        
        ax.set_title(title, color=COLORS["accent"], fontsize=11, 
                     fontweight='bold', pad=10)
    
    def update_data(self, angle: int, distance: int):
        """
        Update with new data point (raw data).
        
        For comparison mode, this should be called with raw data.
        Filtered data is set separately via update_filtered_data().
        """
        self.raw_data[angle] = distance
        self.current_angle = angle
        
        if distance < SENSOR["max_distance"]:
            self.raw_trail.append((math.radians(angle), distance))
        
        self._refresh_display()
    
    def update_filtered_data(self, angle: int, distance: float):
        """Update with filtered data point."""
        self.filtered_data[angle] = distance
        
        if distance < SENSOR["max_distance"]:
            self.filtered_trail.append((math.radians(angle), distance))
    
    def update_stats(self, reduction: float, spikes: int):
        """Update noise reduction statistics."""
        self.noise_stats = {"reduction": reduction, "spikes": spikes}
        self.stats_label.setText(
            f"Avg. Noise Reduction: {reduction:.1f}cm | Spikes Detected: {spikes}"
        )
    
    def _refresh_display(self):
        """Refresh the matplotlib display."""
        # Prepare raw data for plotting
        if self.raw_trail and self.show_raw:
            raw_angles = [p[0] for p in self.raw_trail]
            raw_distances = [p[1] for p in self.raw_trail]
            self.raw_scatter.set_offsets(np.column_stack([raw_angles, raw_distances]))
        else:
            self.raw_scatter.set_offsets(np.empty((0, 2)))
        
        # Prepare filtered data for plotting
        if self.filtered_trail and self.show_filtered:
            filt_angles = [p[0] for p in self.filtered_trail]
            filt_distances = [p[1] for p in self.filtered_trail]
            self.filtered_scatter.set_offsets(np.column_stack([filt_angles, filt_distances]))
        else:
            self.filtered_scatter.set_offsets(np.empty((0, 2)))
        
        self.canvas.draw_idle()
    
    def clear(self):
        """Clear all data."""
        self.raw_data.clear()
        self.filtered_data.clear()
        self.raw_trail.clear()
        self.filtered_trail.clear()
        
        if self.raw_scatter:
            self.raw_scatter.set_offsets(np.empty((0, 2)))
        if self.filtered_scatter:
            self.filtered_scatter.set_offsets(np.empty((0, 2)))
        
        if self.canvas:
            self.canvas.draw_idle()

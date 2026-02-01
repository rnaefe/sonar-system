"""
Polar Radar - Classic sonar-style polar plot visualization
"""

import math
import numpy as np
from collections import deque
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..core.base_radar import BaseRadar
from ..config import SENSOR, DISPLAY, COLORS


class PolarRadar(BaseRadar):
    """
    Classic polar plot radar visualization.
    
    Features:
    - Real-time polar plot (0-180°)
    - Matrix/Sci-Fi aesthetic (black + green)
    - Trail effect for wall visualization
    - Sweep beam animation
    """
    
    NAME = "Polar Radar"
    DESCRIPTION = "Classic sonar-style polar plot with trail effect"
    ICON = "📡"
    
    def __init__(self):
        super().__init__()
        self.trail_data = deque(maxlen=DISPLAY["trail_length"])
        self.current_angle = 0
        self.fig = None
        self.ax = None
        self.canvas = None
        
        # Plot elements
        self.trail_scatter = None
        self.sweep_line = None
        self.current_point = None
        self.beam_line = None
        self.status_text = None
    
    def create_widget(self) -> QWidget:
        """Create the polar radar widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), facecolor=COLORS["background"])
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        # Setup polar plot
        self.ax = self.fig.add_subplot(111, projection='polar', 
                                        facecolor=COLORS["background"])
        
        # Configure for 180° semicircle
        self.ax.set_thetamin(0)
        self.ax.set_thetamax(180)
        self.ax.set_theta_zero_location('S')
        self.ax.set_theta_direction(-1)
        self.ax.set_rlim(0, SENSOR["max_distance"])
        
        # Styling
        self.ax.grid(True, color=COLORS["accent"], alpha=0.3, linewidth=0.5)
        self.ax.tick_params(colors=COLORS["accent"], labelsize=8)
        
        # Distance rings
        r_labels = [50, 100, 150, 200]
        self.ax.set_rticks([r for r in r_labels if r <= SENSOR["max_distance"]])
        self.ax.set_yticklabels([f'{r}cm' for r in r_labels if r <= SENSOR["max_distance"]], 
                                 color=COLORS["accent"], fontsize=8)
        
        # Angle labels
        angle_labels = [0, 30, 60, 90, 120, 150, 180]
        self.ax.set_xticks([math.radians(a) for a in angle_labels])
        self.ax.set_xticklabels([f'{a}°' for a in angle_labels], 
                                 color=COLORS["accent"], fontsize=9)
        
        # Spine styling
        self.ax.spines['polar'].set_color(COLORS["accent"])
        self.ax.spines['polar'].set_linewidth(2)
        
        # Title
        self.ax.set_title('📡 POLAR RADAR', color=COLORS["accent"], 
                          fontsize=14, fontweight='bold', pad=20)
        
        # Create plot elements
        self.trail_scatter = self.ax.scatter([], [], c=[], cmap='Greens', 
                                              s=20, alpha=0.8)
        self.sweep_line, = self.ax.plot([], [], color=COLORS["accent"], 
                                         linewidth=2, alpha=0.9)
        self.current_point, = self.ax.plot([], [], 'o', color=COLORS["accent"], 
                                            markersize=10, markeredgecolor='white', 
                                            markeredgewidth=1)
        self.beam_line, = self.ax.plot([], [], color=COLORS["accent"], 
                                        linewidth=1, alpha=0.5)
        self.status_text = self.ax.text(math.radians(90), SENSOR["max_distance"] * 1.15, 
                                         '', ha='center', va='center', 
                                         color=COLORS["accent"], fontsize=10)
        
        self.widget = widget
        return widget
    
    def update_data(self, angle: int, distance: int):
        """Update radar with new data"""
        self.radar_data[angle] = distance
        self.current_angle = angle
        
        # Add to trail
        if distance < SENSOR["max_distance"]:
            angle_rad = math.radians(angle)
            self.trail_data.append((angle_rad, distance))
        
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the matplotlib display"""
        if self.ax is None:
            return
        
        # Update trail
        if self.trail_data:
            angles = [p[0] for p in self.trail_data]
            distances = [p[1] for p in self.trail_data]
            colors = np.linspace(0.3, 1.0, len(self.trail_data))
            
            self.trail_scatter.set_offsets(np.column_stack([angles, distances]))
            self.trail_scatter.set_array(colors)
        
        # Update sweep line
        if self.radar_data:
            sorted_angles = sorted(self.radar_data.keys())
            line_angles = [math.radians(a) for a in sorted_angles]
            line_distances = [self.radar_data[a] for a in sorted_angles]
            self.sweep_line.set_data(line_angles, line_distances)
        
        # Update current point
        if self.current_angle in self.radar_data:
            dist = self.radar_data[self.current_angle]
            self.current_point.set_data([math.radians(self.current_angle)], [dist])
        
        # Update beam
        self.beam_line.set_data([math.radians(self.current_angle), 
                                  math.radians(self.current_angle)], 
                                 [0, SENSOR["max_distance"]])
        
        # Update status
        if self.current_angle in self.radar_data:
            dist = self.radar_data[self.current_angle]
            self.status_text.set_text(f"Angle: {self.current_angle}° | Distance: {dist}cm")
        
        self.canvas.draw_idle()
    
    def clear(self):
        """Clear all data"""
        self.radar_data.clear()
        self.trail_data.clear()
        if self.trail_scatter:
            self.trail_scatter.set_offsets(np.empty((0, 2)))
        if self.sweep_line:
            self.sweep_line.set_data([], [])
        if self.canvas:
            self.canvas.draw_idle()

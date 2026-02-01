"""
Robot FOV Radar - First person view 2D visualization
"""

import math
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont

from ..core.base_radar import BaseRadar
from ..config import SENSOR, COLORS


class RobotFOVWidget(QWidget):
    """Custom widget for robot FOV visualization"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.radar_data = {}
        self.current_angle = 90
    
    def update_data(self, angle: int, distance: int):
        """Update data"""
        self.radar_data[angle] = distance
        self.current_angle = angle
        self.update()
    
    def clear_data(self):
        """Clear all data"""
        self.radar_data.clear()
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx = w // 2
        cy = h - 40  # Robot at bottom
        
        max_dist = SENSOR["max_distance"]
        scale = min(w // 2 - 20, h - 80) / max_dist
        
        # Background
        painter.fillRect(0, 0, w, h, QColor(COLORS["background"]))
        
        # Draw distance rings
        painter.setPen(QPen(QColor(COLORS["accent"]), 1, Qt.DashLine))
        for r in [25, 50, 75, 100, 150, 200]:
            if r <= max_dist:
                radius = int(r * scale)
                painter.drawArc(cx - radius, cy - radius, 
                               radius * 2, radius * 2, 0, 180 * 16)
                painter.drawText(cx + radius + 5, cy, f"{r}cm")
        
        # Draw angle lines
        painter.setPen(QPen(QColor(COLORS["grid"]), 1))
        for angle in [0, 30, 60, 90, 120, 150, 180]:
            rad = math.radians(angle)
            x = cx + int(max_dist * scale * math.cos(rad))
            y = cy - int(max_dist * scale * math.sin(rad))
            painter.drawLine(cx, cy, x, y)
            painter.drawText(int(x + 5 * math.cos(rad)), int(y - 5 * math.sin(rad)), f"{angle}°")
        
        # Draw FOV area
        painter.setBrush(QBrush(QColor(0, 255, 136, 20)))
        painter.setPen(Qt.NoPen)
        
        # Draw detected obstacles as a connected line
        if self.radar_data:
            points = []
            for angle in sorted(self.radar_data.keys()):
                dist = self.radar_data[angle]
                if dist < max_dist:
                    rad = math.radians(angle)
                    x = cx + int(dist * scale * math.cos(rad))
                    y = cy - int(dist * scale * math.sin(rad))
                    points.append((x, y))
            
            if len(points) >= 2:
                painter.setPen(QPen(QColor(COLORS["accent"]), 3))
                for i in range(len(points) - 1):
                    painter.drawLine(points[i][0], points[i][1], 
                                   points[i+1][0], points[i+1][1])
            
            # Draw points
            painter.setPen(Qt.NoPen)
            for x, y in points:
                painter.setBrush(QBrush(QColor(COLORS["accent"])))
                painter.drawEllipse(x - 4, y - 4, 8, 8)
        
        # Draw current scan beam
        rad = math.radians(self.current_angle)
        beam_x = cx + int(max_dist * scale * math.cos(rad))
        beam_y = cy - int(max_dist * scale * math.sin(rad))
        painter.setPen(QPen(QColor(COLORS["danger"]), 2, Qt.DashLine))
        painter.drawLine(cx, cy, beam_x, beam_y)
        
        # Draw robot
        painter.setBrush(QBrush(QColor(COLORS["accent"])))
        painter.setPen(QPen(QColor(COLORS["text"]), 2))
        painter.drawEllipse(cx - 15, cy - 15, 30, 30)
        
        # Robot direction indicator
        painter.drawLine(cx, cy - 15, cx, cy - 25)
        
        # Draw title
        painter.setPen(QPen(QColor(COLORS["accent"])))
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        painter.drawText(10, 30, "🤖 ROBOT FOV - Front View")
        
        # Draw current reading
        if self.current_angle in self.radar_data:
            dist = self.radar_data[self.current_angle]
            painter.setFont(QFont("Consolas", 12))
            painter.drawText(10, h - 15, f"Angle: {self.current_angle}° | Distance: {dist}cm")


class RobotFOVRadar(BaseRadar):
    """
    Robot First Person View radar.
    
    Features:
    - Shows 180° view from robot's perspective
    - Real-time obstacle visualization
    - Distance lines and wall detection
    - Simple and fast
    """
    
    NAME = "Robot FOV"
    DESCRIPTION = "First person view from robot's perspective"
    ICON = "🤖"
    
    def __init__(self):
        super().__init__()
        self.fov_widget = None
    
    def create_widget(self) -> QWidget:
        """Create the Robot FOV widget"""
        self.fov_widget = RobotFOVWidget()
        self.widget = self.fov_widget
        return self.fov_widget
    
    def update_data(self, angle: int, distance: int):
        """Update radar with new data"""
        self.radar_data[angle] = distance
        if self.fov_widget:
            self.fov_widget.update_data(angle, distance)
    
    def clear(self):
        """Clear all data"""
        self.radar_data.clear()
        if self.fov_widget:
            self.fov_widget.clear_data()

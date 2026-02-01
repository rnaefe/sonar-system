"""
Mini Radar Widget - Small 2D radar map
"""

import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from ..config import SENSOR, COLORS


class MiniRadarWidget(QWidget):
    """
    Small 2D radar map widget.
    Shows a simplified top-down view of the scan area.
    """
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 150)
        self.radar_data = {}
        self.current_angle = 0
    
    def update_data(self, angle: int, distance: int):
        """Update radar data"""
        self.radar_data[angle] = distance
        self.current_angle = angle
        self.update()
    
    def clear_data(self):
        """Clear all data"""
        self.radar_data.clear()
        self.update()
    
    def paintEvent(self, event):
        """Paint the mini radar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h - 10
        radius = min(w // 2 - 10, h - 20)
        
        max_dist = SENSOR["max_distance"]
        
        # Background
        painter.fillRect(0, 0, w, h, QColor(COLORS["panel"]))
        
        # Half circle arc
        painter.setPen(QPen(QColor(COLORS["accent"]), 1))
        painter.drawArc(cx - radius, cy - radius, 
                       radius * 2, radius * 2, 0, 180 * 16)
        
        # Draw obstacles as connected line
        if self.radar_data:
            points = []
            for angle in sorted(self.radar_data.keys()):
                dist = self.radar_data[angle]
                if dist < max_dist:
                    r = int((dist / max_dist) * radius)
                    rad = math.radians(angle)
                    x = cx + int(r * math.cos(rad))
                    y = cy - int(r * math.sin(rad))
                    points.append((x, y))
            
            if len(points) >= 2:
                painter.setPen(QPen(QColor(COLORS["accent"]), 2))
                for i in range(len(points) - 1):
                    painter.drawLine(points[i][0], points[i][1],
                                   points[i+1][0], points[i+1][1])
        
        # Robot marker
        painter.setBrush(QBrush(QColor(COLORS["accent"])))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 5, cy - 5, 10, 10)
        
        # Scan beam
        rad = math.radians(self.current_angle)
        beam_x = cx + int(radius * math.cos(rad))
        beam_y = cy - int(radius * math.sin(rad))
        painter.setPen(QPen(QColor(COLORS["accent"]), 1, Qt.DashLine))
        painter.drawLine(cx, cy, beam_x, beam_y)

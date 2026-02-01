"""
Object Detection Radar - Intelligent object detection and classification
"""

import math
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont

from ..core.base_radar import BaseRadar
from ..config import SENSOR, DETECTION, COLORS


class DetectedObject:
    """Represents a detected object"""
    
    def __init__(self, center_angle: float, avg_distance: float, 
                 min_distance: float, width: float):
        self.center_angle = center_angle
        self.avg_distance = avg_distance
        self.min_distance = min_distance
        self.width = width
        
        # Classify object
        if min_distance <= DETECTION["danger_zone"]:
            self.type = "DANGER"
            self.color = COLORS["danger"]
        elif min_distance <= DETECTION["warning_zone"]:
            self.type = "WARNING"
            self.color = COLORS["warning"]
        else:
            self.type = "SAFE"
            self.color = COLORS["safe"]


class ObjectDetectionWidget(QWidget):
    """Custom widget for object detection visualization"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.radar_data = {}
        self.detected_objects = []
        self.current_angle = 90
    
    def update_data(self, angle: int, distance: int):
        """Update data and detect objects"""
        self.radar_data[angle] = distance
        self.current_angle = angle
        self._detect_objects()
        self.update()
    
    def _detect_objects(self):
        """Detect objects from radar data"""
        self.detected_objects = []
        
        if len(self.radar_data) < 3:
            return
        
        sorted_angles = sorted(self.radar_data.keys())
        current_cluster = []
        
        for angle in sorted_angles:
            distance = self.radar_data[angle]
            
            if distance < SENSOR["max_distance"] - 5:
                if not current_cluster:
                    current_cluster = [(angle, distance)]
                else:
                    last_angle = current_cluster[-1][0]
                    last_dist = current_cluster[-1][1]
                    
                    if (abs(angle - last_angle) <= DETECTION["cluster_threshold"] and 
                        abs(distance - last_dist) <= 30):
                        current_cluster.append((angle, distance))
                    else:
                        self._analyze_cluster(current_cluster)
                        current_cluster = [(angle, distance)]
            else:
                self._analyze_cluster(current_cluster)
                current_cluster = []
        
        self._analyze_cluster(current_cluster)
    
    def _analyze_cluster(self, cluster):
        """Analyze a cluster of points"""
        if len(cluster) < DETECTION["min_object_points"]:
            return
        
        angles = [p[0] for p in cluster]
        distances = [p[1] for p in cluster]
        
        obj = DetectedObject(
            center_angle=sum(angles) / len(angles),
            avg_distance=sum(distances) / len(distances),
            min_distance=min(distances),
            width=max(angles) - min(angles)
        )
        self.detected_objects.append(obj)
    
    def clear_data(self):
        """Clear all data"""
        self.radar_data.clear()
        self.detected_objects.clear()
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx = w // 2
        cy = h - 60
        
        max_dist = SENSOR["max_distance"]
        scale = min(w // 2 - 30, h - 100) / max_dist
        
        # Background
        painter.fillRect(0, 0, w, h, QColor(COLORS["background"]))
        
        # Draw zones
        # Danger zone
        danger_r = int(DETECTION["danger_zone"] * scale)
        painter.setBrush(QBrush(QColor(255, 50, 100, 40)))
        painter.setPen(Qt.NoPen)
        painter.drawPie(cx - danger_r, cy - danger_r, 
                       danger_r * 2, danger_r * 2, 0, 180 * 16)
        
        # Warning zone
        warning_r = int(DETECTION["warning_zone"] * scale)
        painter.setBrush(QBrush(QColor(255, 170, 0, 30)))
        painter.drawPie(cx - warning_r, cy - warning_r, 
                       warning_r * 2, warning_r * 2, 0, 180 * 16)
        
        # Distance rings
        painter.setPen(QPen(QColor(COLORS["accent"]), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        for r in [25, 50, 75, 100, 150, 200]:
            if r <= max_dist:
                radius = int(r * scale)
                painter.drawArc(cx - radius, cy - radius, 
                               radius * 2, radius * 2, 0, 180 * 16)
        
        # Draw detected objects
        for obj in self.detected_objects:
            rad = math.radians(obj.center_angle)
            x = cx + int(obj.avg_distance * scale * math.cos(rad))
            y = cy - int(obj.avg_distance * scale * math.sin(rad))
            
            # Object marker
            painter.setBrush(QBrush(QColor(obj.color)))
            painter.setPen(QPen(QColor(COLORS["text"]), 2))
            size = max(10, int(obj.width * 2))
            painter.drawRect(x - size//2, y - size//2, size, size)
            
            # Object label
            painter.setPen(QPen(QColor(obj.color)))
            painter.setFont(QFont("Consolas", 9, QFont.Bold))
            painter.drawText(x - 20, y - size//2 - 5, 
                           f"{int(obj.min_distance)}cm")
        
        # Draw scan beam
        rad = math.radians(self.current_angle)
        beam_x = cx + int(max_dist * scale * math.cos(rad))
        beam_y = cy - int(max_dist * scale * math.sin(rad))
        painter.setPen(QPen(QColor(COLORS["accent"]), 1, Qt.DashLine))
        painter.drawLine(cx, cy, beam_x, beam_y)
        
        # Draw robot
        painter.setBrush(QBrush(QColor(COLORS["accent"])))
        painter.setPen(QPen(QColor(COLORS["text"]), 2))
        painter.drawEllipse(cx - 15, cy - 15, 30, 30)
        
        # Title
        painter.setPen(QPen(QColor(COLORS["accent"])))
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        painter.drawText(10, 30, "🎯 OBJECT DETECTION RADAR")
        
        # Stats
        painter.setFont(QFont("Consolas", 11))
        danger_count = sum(1 for o in self.detected_objects if o.type == "DANGER")
        warning_count = sum(1 for o in self.detected_objects if o.type == "WARNING")
        safe_count = sum(1 for o in self.detected_objects if o.type == "SAFE")
        
        y_offset = 55
        painter.setPen(QPen(QColor(COLORS["danger"])))
        painter.drawText(10, y_offset, f"⚠️ DANGER: {danger_count}")
        painter.setPen(QPen(QColor(COLORS["warning"])))
        painter.drawText(10, y_offset + 20, f"⚡ WARNING: {warning_count}")
        painter.setPen(QPen(QColor(COLORS["safe"])))
        painter.drawText(10, y_offset + 40, f"✓ SAFE: {safe_count}")
        
        # Zone legend
        painter.setFont(QFont("Consolas", 9))
        painter.setPen(QPen(QColor(COLORS["danger"])))
        painter.drawText(w - 120, y_offset, f"Danger: <{DETECTION['danger_zone']}cm")
        painter.setPen(QPen(QColor(COLORS["warning"])))
        painter.drawText(w - 120, y_offset + 15, f"Warning: <{DETECTION['warning_zone']}cm")


class ObjectDetectionRadar(BaseRadar):
    """
    Object Detection Radar with classification.
    
    Features:
    - Real-time object detection
    - Object classification (danger/warning/safe)
    - Box visualization for objects
    - Distance and angle labels
    - Warning system for close objects
    """
    
    NAME = "Object Detection"
    DESCRIPTION = "Intelligent object detection with zone classification"
    ICON = "🎯"
    
    def __init__(self):
        super().__init__()
        self.detection_widget = None
    
    def create_widget(self) -> QWidget:
        """Create the Object Detection widget"""
        self.detection_widget = ObjectDetectionWidget()
        self.widget = self.detection_widget
        return self.detection_widget
    
    def update_data(self, angle: int, distance: int):
        """Update radar with new data"""
        self.radar_data[angle] = distance
        if self.detection_widget:
            self.detection_widget.update_data(angle, distance)
    
    def clear(self):
        """Clear all data"""
        self.radar_data.clear()
        if self.detection_widget:
            self.detection_widget.clear_data()
    
    def get_detected_objects(self) -> list:
        """Get list of detected objects"""
        if self.detection_widget:
            return self.detection_widget.detected_objects
        return []

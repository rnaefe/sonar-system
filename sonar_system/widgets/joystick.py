"""
Joystick Widget - Virtual joystick for robot control
"""

import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

from ..config import COLORS


class JoystickWidget(QWidget):
    """
    Virtual joystick widget for robot control.
    
    Signals:
        moved(x: float, y: float): Emitted when joystick moves (-1 to 1)
    """
    
    moved = pyqtSignal(float, float)
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(180, 180)
        self.setMaximumSize(180, 180)
        self.x = 0.0
        self.y = 0.0
        self.pressed = False
    
    def paintEvent(self, event):
        """Paint the joystick"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        radius = min(w, h) // 2 - 10
        
        # Outer circle
        painter.setPen(QPen(QColor(COLORS["accent"]), 2))
        painter.setBrush(QBrush(QColor(COLORS["panel"])))
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
        
        # Cross lines
        painter.setPen(QPen(QColor(COLORS["grid"]), 1))
        painter.drawLine(cx - radius, cy, cx + radius, cy)
        painter.drawLine(cx, cy - radius, cx, cy + radius)
        
        # Joystick knob
        knob_x = cx + int(self.x * radius * 0.8)
        knob_y = cy - int(self.y * radius * 0.8)
        knob_r = 22
        
        gradient = QLinearGradient(knob_x - knob_r, knob_y - knob_r,
                                    knob_x + knob_r, knob_y + knob_r)
        gradient.setColorAt(0, QColor(COLORS["accent"]))
        gradient.setColorAt(1, QColor(COLORS["accent_dark"]))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(COLORS["text"]), 2))
        painter.drawEllipse(knob_x - knob_r, knob_y - knob_r, knob_r * 2, knob_r * 2)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.pressed = True
        self._update_position(event.pos())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.pressed:
            self._update_position(event.pos())
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.pressed = False
        self.x = 0.0
        self.y = 0.0
        self.moved.emit(0.0, 0.0)
        self.update()
    
    def _update_position(self, pos):
        """Update joystick position from mouse position"""
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        radius = min(w, h) // 2 - 10
        
        dx = (pos.x() - cx) / radius
        dy = -(pos.y() - cy) / radius
        
        # Keep inside circle
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 1:
            dx /= dist
            dy /= dist
        
        self.x = max(-1, min(1, dx))
        self.y = max(-1, min(1, dy))
        
        self.moved.emit(self.x, self.y)
        self.update()

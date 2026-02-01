"""
3D LiDAR Radar - Real-time 3D point cloud visualization with tunnel effect
"""

import math
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph.opengl as gl

from ..core.base_radar import BaseRadar
from ..config import SENSOR, LIDAR_3D, COLORS


class ScanData:
    """Manages scan data with rolling buffer for tunnel effect"""
    
    def __init__(self, max_layers: int = 100, z_shift: int = 5):
        self.max_layers = max_layers
        self.z_shift = z_shift
        self.current_sweep = {}
        self.point_cloud = []
        self.last_angle = -1
        self.sweep_direction = 1
    
    def add_point(self, angle: int, distance: int):
        """Add a new scan point"""
        if self.last_angle >= 0:
            if angle < self.last_angle and self.sweep_direction == 1:
                self._finalize_sweep()
                self.sweep_direction = -1
            elif angle > self.last_angle and self.sweep_direction == -1:
                self._finalize_sweep()
                self.sweep_direction = 1
        
        self.last_angle = angle
        self.current_sweep[angle] = distance
    
    def _finalize_sweep(self):
        """Convert current sweep to 3D points"""
        if not self.current_sweep:
            return
        
        for layer in self.point_cloud:
            layer[:, 2] -= self.z_shift
        
        self.point_cloud = [p for p in self.point_cloud 
                           if np.max(p[:, 2]) > -self.max_layers * self.z_shift]
        
        new_points = []
        for angle, distance in self.current_sweep.items():
            if 0 < distance <= SENSOR["max_distance"]:
                angle_rad = math.radians(angle)
                x = distance * math.cos(angle_rad)
                y = distance * math.sin(angle_rad)
                new_points.append([x, y, 0])
        
        if new_points:
            self.point_cloud.append(np.array(new_points, dtype=np.float32))
        
        self.current_sweep.clear()
    
    def get_all_points(self) -> np.ndarray:
        """Get all points as numpy array"""
        if not self.point_cloud:
            return np.zeros((0, 3), dtype=np.float32)
        
        current = []
        for angle, distance in self.current_sweep.items():
            if 0 < distance <= SENSOR["max_distance"]:
                angle_rad = math.radians(angle)
                x = distance * math.cos(angle_rad)
                y = distance * math.sin(angle_rad)
                current.append([x, y, 0])
        
        layers = self.point_cloud.copy()
        if current:
            layers.append(np.array(current, dtype=np.float32))
        
        if layers:
            return np.vstack(layers)
        return np.zeros((0, 3), dtype=np.float32)
    
    def get_colors(self, points: np.ndarray) -> np.ndarray:
        """Generate colors with depth-based fade"""
        if len(points) == 0:
            return np.zeros((0, 4), dtype=np.float32)
        
        colors = np.zeros((len(points), 4), dtype=np.float32)
        z_values = points[:, 2]
        z_min = z_values.min() if len(z_values) > 0 else 0
        z_range = -z_min if z_min != 0 else 1
        
        alpha = (z_values - z_min) / z_range if z_range != 0 else np.ones_like(z_values)
        alpha = np.clip(alpha, 0.2, 1.0)
        
        colors[:, 0] = 0.0   # R
        colors[:, 1] = 1.0   # G
        colors[:, 2] = 0.5   # B
        colors[:, 3] = alpha
        
        return colors
    
    def clear(self):
        """Clear all data"""
        self.current_sweep.clear()
        self.point_cloud.clear()
        self.last_angle = -1


class Lidar3DRadar(BaseRadar):
    """
    3D LiDAR point cloud visualization.
    
    Features:
    - Real-time 3D point cloud rendering
    - "Tunnel Effect" - history extends into Z-axis depth
    - Neon green aesthetic on black background
    - Mouse interaction: rotate, zoom, pan
    """
    
    NAME = "3D LiDAR"
    DESCRIPTION = "Real-time 3D point cloud with tunnel effect"
    ICON = "🌐"
    
    def __init__(self):
        super().__init__()
        self.scan_data = ScanData(
            max_layers=LIDAR_3D["max_history_layers"],
            z_shift=LIDAR_3D["z_shift_amount"]
        )
        self.view = None
        self.scatter = None
        self.grid = None
    
    def create_widget(self) -> QWidget:
        """Create the 3D LiDAR widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create OpenGL view
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor(COLORS["background"])
        self.view.setCameraPosition(distance=150, elevation=30, azimuth=90)
        layout.addWidget(self.view)
        
        # Add grid
        self.grid = gl.GLGridItem()
        self.grid.setSize(200, 200)
        self.grid.setSpacing(10, 10)
        self.grid.setColor((0, 100, 0, 100))
        self.view.addItem(self.grid)
        
        # Create scatter plot for points
        self.scatter = gl.GLScatterPlotItem()
        self.scatter.setGLOptions('translucent')
        self.view.addItem(self.scatter)
        
        # Add robot marker
        robot_mesh = gl.GLMeshItem(
            meshdata=gl.MeshData.sphere(rows=10, cols=10, radius=3),
            color=(0, 1, 0.5, 0.8),
            smooth=True
        )
        self.view.addItem(robot_mesh)
        
        # Add forward direction indicator
        arrow = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, 30, 0]]),
            color=(0, 1, 0, 0.7),
            width=3
        )
        self.view.addItem(arrow)
        
        self.widget = widget
        return widget
    
    def update_data(self, angle: int, distance: int):
        """Update radar with new data"""
        self.radar_data[angle] = distance
        self.scan_data.add_point(angle, distance)
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the 3D display"""
        if self.scatter is None:
            return
        
        points = self.scan_data.get_all_points()
        
        if len(points) > 0:
            colors = self.scan_data.get_colors(points)
            self.scatter.setData(pos=points, color=colors, size=4)
    
    def clear(self):
        """Clear all data"""
        self.radar_data.clear()
        self.scan_data.clear()
        if self.scatter:
            self.scatter.setData(pos=np.zeros((0, 3)))

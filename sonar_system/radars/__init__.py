"""
Radars Package - All radar visualization plugins
"""
from .polar_radar import PolarRadar
from .lidar_3d_radar import Lidar3DRadar
from .robot_fov_radar import RobotFOVRadar
from .object_detection_radar import ObjectDetectionRadar
from .comparison_radar import ComparisonRadar

# Registry of all available radars
AVAILABLE_RADARS = [
    PolarRadar,
    Lidar3DRadar,
    RobotFOVRadar,
    ObjectDetectionRadar,
    ComparisonRadar,
]

def get_radar_by_name(name: str):
    """Get radar class by name"""
    for radar_class in AVAILABLE_RADARS:
        if radar_class.NAME == name:
            return radar_class
    return None

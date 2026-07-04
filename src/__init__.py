"""
Meme Face Detector - Real-time face expression and gesture detection with meme overlay

This package contains modules for:
- Camera input management
- Face and hand detection (MediaPipe)
- Expression and gesture analysis
- Meme selection and overlay
- Display output
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .camera import Camera
from .detector import FaceDetector
from .expression_analyzer import ExpressionAnalyzer
from .meme_selector import MemeSelector
from .overlay import MemeOverlay
from .display import Display

__all__ = [
    "Camera",
    "FaceDetector",
    "ExpressionAnalyzer",
    "MemeSelector",
    "MemeOverlay",
    "Display",
]

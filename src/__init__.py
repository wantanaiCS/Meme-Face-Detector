"""
Meme Face Detector - Real-time face expression and gesture detection with meme overlay

Modules:
- camera              : Camera input management
- detector            : Face and hand detection (MediaPipe)
- expression_analyzer : Expression and gesture analysis
- meme_selector       : Meme selection with cooldown
- overlay             : Image overlay with alpha blending
- display             : Display output and FPS counter
"""

__version__ = "0.2.0"
__author__  = "Meme Face Detector"

from .camera              import Camera
from .detector            import FaceDetector
from .expression_analyzer import ExpressionAnalyzer
from .meme_selector       import MemeSelector
from .overlay             import MemeOverlay
from .display             import Display

__all__ = [
    "Camera",
    "FaceDetector",
    "ExpressionAnalyzer",
    "MemeSelector",
    "MemeOverlay",
    "Display",
]

# 🛠️ Development Guide

คู่มือสำหรับการพัฒนาและขยายฟีเจอร์โปรเจค Meme Face Detector

---

## 🚀 เริ่มต้นพัฒนา

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/yourusername/meme-face-detector.git
cd meme-face-detector

# สร้าง virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 2. โครงสร้างโค้ด

```
src/
├── __init__.py              # Package initializer
├── camera.py                # Camera input
├── detector.py              # MediaPipe face/hand detection
├── expression_analyzer.py   # Expression analysis logic
├── meme_selector.py         # Meme selection engine
├── overlay.py               # Image overlay
└── display.py               # Display output
```

---

## 📝 Coding Standards

### Python Style Guide

ใช้ **PEP 8** style guide:

```python
# ✅ Good
def calculate_mouth_open(face_landmarks, frame_shape):
    """Calculate mouth opening distance."""
    pass

# ❌ Bad
def CalculateMouthOpen(FaceLandmarks, FrameShape):
    pass
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Class | PascalCase | `FaceDetector` |
| Function | snake_case | `detect_faces()` |
| Variable | snake_case | `mouth_open` |
| Constant | UPPER_SNAKE_CASE | `MAX_NUM_FACES` |
| Private | _leading_underscore | `_calculate_distance()` |

### Type Hints

ใช้ type hints เสมอ:

```python
from typing import Tuple, Optional
import numpy as np

def get_landmark_coords(
    face_landmarks: Any,
    index: int,
    frame_shape: Tuple[int, int, int]
) -> Tuple[int, int]:
    """Extract landmark coordinates."""
    pass
```

### Docstrings

ใช้ Google style docstrings:

```python
def analyze_expression(face_landmarks, frame_shape):
    """
    Analyze facial expression from landmarks.
    
    Args:
        face_landmarks: MediaPipe face landmarks object
        frame_shape: Tuple of (height, width, channels)
    
    Returns:
        str: Expression name (e.g., "happy", "surprised")
    
    Raises:
        ValueError: If face_landmarks is None
    
    Example:
        >>> expression = analyzer.analyze_expression(landmarks, (480, 640, 3))
        >>> print(expression)
        'happy'
    """
    pass
```

---

## 🔧 เพิ่มฟีเจอร์ใหม่

### 1. เพิ่มท่าทางใหม่

**ขั้นตอน:**

1. **อัปเดต config/expression_rules.json**
```json
{
  "winking": {
    "description": "ขยิบตา",
    "left_eye_open_min": 0.2,
    "right_eye_open_max": 0.1
  }
}
```

2. **เพิ่มฟังก์ชันวิเคราะห์ใน expression_analyzer.py**
```python
def _detect_winking(self, face_landmarks, frame_shape):
    left_ear = self._calculate_eye_aspect_ratio(face_landmarks, "left")
    right_ear = self._calculate_eye_aspect_ratio(face_landmarks, "right")
    
    if left_ear > 0.2 and right_ear < 0.1:
        return "winking"
    return None
```

3. **เพิ่มใน analyze_expression()**
```python
def analyze_expression(self, face_landmarks, frame_shape):
    # ... existing checks ...
    
    winking = self._detect_winking(face_landmarks, frame_shape)
    if winking:
        return winking
    
    # ... rest of checks ...
```

4. **อัปเดต config/meme_mapping.json**
```json
{
  "winking": "winking"
}
```

5. **สร้างโฟลเดอร์และเพิ่ม Meme**
```bash
mkdir memes/winking
# วางภาพ Meme ลงในโฟลเดอร์
```

### 2. เพิ่ม Gesture ใหม่

ขั้นตอนคล้ายกับการเพิ่มท่าทาง แต่แก้ใน `analyze_gesture()` แทน

---

## 🧪 Testing

### Manual Testing

```python
# examples/test_camera.py
from src.camera import Camera

camera = Camera(camera_id=0)
while True:
    frame = camera.read_frame()
    if frame is None:
        break
    cv2.imshow("Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera.release()
```

### Unit Testing (Optional)

```python
# tests/test_expression_analyzer.py
import unittest
from src.expression_analyzer import ExpressionAnalyzer

class TestExpressionAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ExpressionAnalyzer()
    
    def test_mouth_open_calculation(self):
        # Mock data
        pass
```

---

## 🐛 Debugging Tips

### 1. Visual Debugging

วาด landmarks บนภาพเพื่อดูว่าตรวจจับถูกต้องหรือไม่:

```python
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# วาด face mesh
mp_drawing.draw_landmarks(
    image=frame,
    landmark_list=face_landmarks,
    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
    landmark_drawing_spec=None,
    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
)
```

### 2. Print Debug Values

```python
# ใน expression_analyzer.py
def analyze_expression(self, face_landmarks, frame_shape):
    mouth_open = self._calculate_mouth_open(face_landmarks, frame_shape)
    
    # Debug
    print(f"DEBUG: mouth_open = {mouth_open:.2f}px")
    
    if mouth_open > 25:
        return "surprised"
```

### 3. Calibration Tool

สร้างโปรแกรมแสดงค่าแบบ real-time:

```python
# examples/calibration_tool.py
# (ดู technical-reference.md สำหรับโค้ดเต็ม)
```

---

## 📊 Performance Optimization

### 1. Profiling

```python
import time

start = time.time()
results = face_mesh.process(rgb)
end = time.time()

print(f"Detection took: {(end - start) * 1000:.2f}ms")
```

### 2. Optimization Checklist

- [ ] ลดความละเอียดกล้อง (640x480 แทน 1920x1080)
- [ ] Skip frames (ประมวลผลทุก 2 frames)
- [ ] Pre-load memes แทนการโหลดทุกครั้ง
- [ ] ปิด refine_landmarks ถ้าไม่จำเป็น
- [ ] ใช้ max_num_faces=1

---

## 🔄 Git Workflow

### Branch Strategy

```
main           # Stable version
├── dev        # Development
├── feature/*  # New features
└── fix/*      # Bug fixes
```

### Commit Message Format

```
<type>: <subject>

<body> (optional)

Types:
- feat: ฟีเจอร์ใหม่
- fix: แก้บัก
- docs: เอกสาร
- refactor: ปรับโครงสร้างโค้ด
- perf: ปรับปรุงประสิทธิภาพ
- test: เพิ่ม/แก้ไขเทส
- chore: งานบำรุงรักษา

Examples:
feat: add winking detection
fix: camera not releasing properly
docs: update README with installation steps
```

### Pull Request Template

```markdown
## Description
สรุปสั้นๆ ว่าเปลี่ยนแปลงอะไร

## Changes
- เพิ่ม X
- แก้ไข Y
- ลบ Z

## Testing
- [ ] Tested locally
- [ ] All expressions work
- [ ] No performance regression

## Screenshots (if applicable)
```

---

## 📚 Additional Resources

### MediaPipe
- [Face Mesh Guide](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [Hands Guide](https://google.github.io/mediapipe/solutions/hands.html)

### OpenCV
- [Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

### Python
- [PEP 8 Style Guide](https://pep8.org/)
- [Type Hints](https://docs.python.org/3/library/typing.html)

---

## 🤝 Contributing

1. Fork repository
2. สร้าง feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. เปิด Pull Request

---

## 📞 Support

หากมีคำถามหรือพบปัญหา:
1. เช็ค [technical-reference.md](.kiro/steering/technical-reference.md)
2. อ่าน [meme-face-detector.md](meme-face-detector.md)
3. เปิด GitHub Issue

---

**Happy Coding! 💻**

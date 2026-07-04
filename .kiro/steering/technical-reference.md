---
inclusion: manual
---

# 🔬 Technical Reference — ข้อมูลทางเทคนิคเชิงลึก

> เอกสารนี้เป็น reference สำหรับข้อมูลทางเทคนิคที่ต้องใช้บ่อยในการพัฒนา (Activate ด้วย #technical-reference)

---

## 📍 MediaPipe Face Mesh Landmarks

### จุด Landmark สำคัญ (จากทั้งหมด 468 จุด)

```python
# Mouth (ปาก)
MOUTH_UPPER_CENTER = 13      # ริมฝีปากบนกลาง
MOUTH_LOWER_CENTER = 14      # ริมฝีปากล่างกลาง
MOUTH_LEFT_CORNER = 61       # มุมปากซ้าย
MOUTH_RIGHT_CORNER = 291     # มุมปากขวา

# Eyes (ตา)
RIGHT_EYE_UPPER = 159        # ตาขวาบน
RIGHT_EYE_LOWER = 145        # ตาขวาล่าง
LEFT_EYE_UPPER = 386         # ตาซ้ายบน
LEFT_EYE_LOWER = 374         # ตาซ้ายล่าง

RIGHT_EYE_INNER = 133        # หัวตาขวา (ใกล้จมูก)
RIGHT_EYE_OUTER = 33         # หางตาขวา
LEFT_EYE_INNER = 362         # หัวตาซ้าย (ใกล้จมูก)
LEFT_EYE_OUTER = 263         # หางตาซ้าย

# Eyebrows (คิ้ว)
RIGHT_EYEBROW_INNER = 70     # คิ้วขวาด้านใน
RIGHT_EYEBROW_MID = 63       # คิ้วขวากลาง
RIGHT_EYEBROW_OUTER = 105    # คิ้วขวาด้านนอก

LEFT_EYEBROW_INNER = 300     # คิ้วซ้ายด้านใน
LEFT_EYEBROW_MID = 296       # คิ้วซ้ายกลาง
LEFT_EYEBROW_OUTER = 334     # คิ้วซ้ายด้านนอก

# Nose (จมูก)
NOSE_TIP = 1                 # ปลายจมูก
NOSE_BRIDGE = 6              # สันจมูก

# Face outline (ขอบหน้า)
CHIN = 152                   # คาง
FOREHEAD = 10                # หน้าผาก
```

### Code Example: Extract Landmarks

```python
def get_landmark_coords(face_landmarks, index, frame_shape):
    """
    แปลง normalized coordinates เป็น pixel coordinates
    
    Args:
        face_landmarks: MediaPipe face landmarks object
        index: landmark index (0-467)
        frame_shape: (height, width, channels)
    
    Returns:
        (x, y) ในหน่วย pixels
    """
    h, w = frame_shape[:2]
    landmark = face_landmarks.landmark[index]
    x = int(landmark.x * w)
    y = int(landmark.y * h)
    return (x, y)

# ใช้งาน
mouth_upper = get_landmark_coords(face_landmarks, 13, frame.shape)
mouth_lower = get_landmark_coords(face_landmarks, 14, frame.shape)
mouth_open_pixels = abs(mouth_upper[1] - mouth_lower[1])
```

---

## 🖐️ MediaPipe Hands Landmarks

### จุด Landmark มือ (21 จุด)

```python
# Wrist (ข้อมือ)
WRIST = 0

# Thumb (นิ้วโป้ง) — 4 จุด
THUMB_CMC = 1           # ข้อต่อฐาน
THUMB_MCP = 2           # ข้อต่อกลาง
THUMB_IP = 3            # ข้อต่อบน
THUMB_TIP = 4           # ปลายนิ้ว

# Index finger (นิ้วชี้) — 4 จุด
INDEX_MCP = 5           # ข้อต่อฐาน
INDEX_PIP = 6           # ข้อต่อกลาง
INDEX_DIP = 7           # ข้อต่อบน
INDEX_TIP = 8           # ปลายนิ้ว

# Middle finger (นิ้วกลาง) — 4 จุด
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_DIP = 11
MIDDLE_TIP = 12

# Ring finger (นิ้วนาง) — 4 จุด
RING_MCP = 13
RING_PIP = 14
RING_DIP = 15
RING_TIP = 16

# Pinky (นิ้วก้อย) — 4 จุด
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20
```

### Gesture Detection Logic

```python
def is_finger_extended(hand_landmarks, finger_tip_idx, finger_pip_idx):
    """
    เช็คว่านิ้วยื่นหรือพับ
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        finger_tip_idx: index ของปลายนิ้ว
        finger_pip_idx: index ของข้อนิ้วกลาง
    
    Returns:
        True ถ้านิ้วยื่น (tip อยู่สูงกว่า pip)
    """
    tip = hand_landmarks.landmark[finger_tip_idx]
    pip = hand_landmarks.landmark[finger_pip_idx]
    return tip.y < pip.y  # y น้อย = สูงกว่า

# ตัวอย่างการใช้งาน
index_extended = is_finger_extended(hand_landmarks, 8, 6)
middle_extended = is_finger_extended(hand_landmarks, 12, 10)
ring_extended = is_finger_extended(hand_landmarks, 16, 14)
pinky_extended = is_finger_extended(hand_landmarks, 20, 18)

# ตรวจจับ peace sign (V)
if index_extended and middle_extended and not ring_extended and not pinky_extended:
    gesture = "peace"
```

---

## 🧮 Expression Calculation Formulas

### 1. Mouth Open Distance

```python
def calculate_mouth_open(face_landmarks, frame_shape):
    """
    คำนวณระยะเปิดปาก (แนวตั้ง)
    
    Returns:
        float: ระยะในหน่วย pixels
    """
    h, w = frame_shape[:2]
    upper = face_landmarks.landmark[13]
    lower = face_landmarks.landmark[14]
    
    distance = abs(upper.y - lower.y) * h
    return distance

# Interpretation:
# < 5 pixels   = ปากปิดสนิท
# 5-20 pixels  = ปากเปิดเล็กน้อย (ยิ้ม)
# > 25 pixels  = ปากเปิดกว้าง (ประหลาดใจ/ร้องโวย)
```

### 2. Mouth Smile Detection

```python
def calculate_mouth_smile(face_landmarks, frame_shape):
    """
    คำนวณความยิ้ม (มุมปากยกขึ้น)
    
    Returns:
        float: ratio การยกมุมปาก (0.0 - 1.0+)
    """
    h, w = frame_shape[:2]
    
    # มุมปากซ้ายและขวา
    left_corner = face_landmarks.landmark[61]
    right_corner = face_landmarks.landmark[291]
    mouth_upper = face_landmarks.landmark[13]
    
    # คำนวณว่ามุมปากยกสูงกว่าริมฝีปากบนเท่าไหร่
    avg_corner_y = (left_corner.y + right_corner.y) / 2
    smile_ratio = (mouth_upper.y - avg_corner_y)
    
    return smile_ratio

# Interpretation:
# < -0.01  = ยิ้มเล็กน้อย
# < -0.02  = ยิ้มชัด
```

### 3. Eye Open Detection

```python
def calculate_eye_aspect_ratio(face_landmarks, eye_indices):
    """
    คำนวณ Eye Aspect Ratio (EAR)
    
    Args:
        eye_indices: [upper, lower, inner, outer] landmark indices
    
    Returns:
        float: EAR value (0.0 = ปิด, 0.3+ = เปิด)
    """
    upper_idx, lower_idx, inner_idx, outer_idx = eye_indices
    
    upper = face_landmarks.landmark[upper_idx]
    lower = face_landmarks.landmark[lower_idx]
    inner = face_landmarks.landmark[inner_idx]
    outer = face_landmarks.landmark[outer_idx]
    
    # แนวตั้ง
    vertical_dist = abs(upper.y - lower.y)
    
    # แนวนอน
    horizontal_dist = abs(outer.x - inner.x)
    
    # EAR = vertical / horizontal
    ear = vertical_dist / (horizontal_dist + 1e-6)
    
    return ear

# Right eye
right_eye_ear = calculate_eye_aspect_ratio(
    face_landmarks,
    [159, 145, 133, 33]  # upper, lower, inner, outer
)

# Left eye
left_eye_ear = calculate_eye_aspect_ratio(
    face_landmarks,
    [386, 374, 362, 263]
)

# Average
avg_ear = (right_eye_ear + left_eye_ear) / 2

# Interpretation:
# < 0.15 = ตาหลับ (sleepy/blink)
# > 0.2  = ตาเปิดปกติ
```

### 4. Eyebrow Position

```python
def calculate_eyebrow_raise(face_landmarks, frame_shape):
    """
    คำนวณว่าคิ้วยกสูงหรือไม่
    
    Returns:
        float: ระยะห่างระหว่างคิ้วกับตา (pixels)
    """
    h = frame_shape[0]
    
    # คิ้วขวา
    brow = face_landmarks.landmark[70]
    eye = face_landmarks.landmark[159]
    
    distance = abs(brow.y - eye.y) * h
    
    return distance

# Interpretation:
# < 10 pixels  = คิ้วลงปกติ
# 10-15 pixels = คิ้วตำแหน่งปกติ
# > 15 pixels  = คิ้วยกสูง (ประหลาดใจ)
```

### 5. Head Tilt Detection

```python
def calculate_head_tilt(face_landmarks):
    """
    คำนวณการเอียงหัว
    
    Returns:
        float: องศาการเอียง (degrees)
    """
    # ใช้ตาซ้ายและขวาเป็นจุดอ้างอิง
    left_eye = face_landmarks.landmark[362]
    right_eye = face_landmarks.landmark[133]
    
    # คำนวณมุม
    delta_x = right_eye.x - left_eye.x
    delta_y = right_eye.y - left_eye.y
    
    import math
    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)
    
    return abs(angle_deg)

# Interpretation:
# < 5 degrees  = หัวตรง
# > 10 degrees = หัวเอียง (thinking/curious)
```

---

## 🎨 Image Overlay Techniques

### 1. Overlay with Alpha Channel (PNG)

```python
import cv2
import numpy as np

def overlay_transparent(background, overlay, x, y):
    """
    วางภาพโปร่งใส (RGBA) บน background
    
    Args:
        background: ภาพพื้นหลัง (BGR)
        overlay: ภาพที่จะวางซ้อน (BGRA)
        x, y: ตำแหน่งซ้ายบน
    """
    h, w = overlay.shape[:2]
    
    # ตรวจสอบขอบเขต
    if x + w > background.shape[1] or y + h > background.shape[0]:
        return background
    
    # แยก alpha channel
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        overlay_rgb = overlay[:, :, :3]
    else:
        alpha = np.ones((h, w))
        overlay_rgb = overlay
    
    # ROI (Region of Interest)
    roi = background[y:y+h, x:x+w]
    
    # Alpha blending
    for c in range(3):
        roi[:, :, c] = (
            alpha * overlay_rgb[:, :, c] +
            (1 - alpha) * roi[:, :, c]
        )
    
    background[y:y+h, x:x+w] = roi
    return background
```

### 2. Resize with Aspect Ratio

```python
def resize_with_aspect_ratio(image, width=None, height=None):
    """
    ปรับขนาดภาพโดยรักษาสัดส่วน
    """
    (h, w) = image.shape[:2]
    
    if width is None and height is None:
        return image
    
    if width is None:
        ratio = height / float(h)
        dim = (int(w * ratio), height)
    else:
        ratio = width / float(w)
        dim = (width, int(h * ratio))
    
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
```

---

## ⚡ Performance Optimization Tips

### 1. Reduce Resolution

```python
# แทนที่จะใช้ 1920x1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# ลดเป็น 1280x720 หรือ 640x480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ลด processing time ได้ประมาณ 2-3 เท่า
```

### 2. Skip Frames

```python
# ประมวลผลทุก frame
while True:
    frame = camera.read_frame()
    results = detector.detect_faces(frame)  # ช้า
    display.show(frame)

# ประมวลผลข้าม 1 frame (เร็วขึ้น 2 เท่า)
frame_count = 0
cached_result = None

while True:
    frame = camera.read_frame()
    
    if frame_count % 2 == 0:
        cached_result = detector.detect_faces(frame)
    
    # ใช้ผลลัพธ์ที่ cache ไว้
    # ... process with cached_result
    
    display.show(frame)
    frame_count += 1
```

### 3. Reduce Model Complexity

```python
# แทนที่จะใช้ Face Mesh แบบเต็ม (468 จุด)
face_mesh = mp.solutions.face_mesh.FaceMesh(
    refine_landmarks=True  # รวม iris landmarks
)

# ใช้แบบธรรมดา (ลดเวลาประมวลผล)
face_mesh = mp.solutions.face_mesh.FaceMesh(
    refine_landmarks=False
)
```

### 4. Optimize Meme Loading

```python
# ❌ โหลดภาพทุกครั้งที่เลือก Meme
def select_and_load_meme(expression):
    path = get_meme_path(expression)
    meme = cv2.imread(path)  # ช้า!
    return meme

# ✅ Pre-load และ cache
class MemeSelector:
    def __init__(self):
        self.cache = {}
        self._preload_memes()
    
    def _preload_memes(self):
        """โหลด Meme ทั้งหมดตอนเริ่มโปรแกรม"""
        for category in os.listdir("memes/"):
            category_path = f"memes/{category}"
            for filename in os.listdir(category_path):
                path = os.path.join(category_path, filename)
                self.cache[path] = cv2.imread(path, cv2.IMREAD_UNCHANGED)
```

---

## 🐛 Common Errors & Solutions

### Error 1: Camera Won't Open

```python
# ข้อผิดพลาด:
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
# ret = False, frame = None

# สาเหตุ + แก้ไข:
# 1. กล้องถูกโปรแกรมอื่นใช้งาน → ปิดโปรแกรมนั้น
# 2. ใช้ camera_id ผิด → ลอง 0, 1, 2
# 3. Permission denied → เช็คการอนุญาตใน Privacy Settings

# แก้:
for camera_id in range(3):
    cap = cv2.VideoCapture(camera_id)
    if cap.isOpened():
        print(f"Camera {camera_id} works!")
        break
    cap.release()
```

### Error 2: MediaPipe Returns None

```python
# ข้อผิดพลาด:
results = face_mesh.process(frame)
if results.multi_face_landmarks:  # None!

# สาเหตุ:
# 1. ส่ง BGR แทน RGB → แปลงก่อน
# 2. แสงน้อยเกินไป
# 3. ใบหน้าเล็กเกินไป

# แก้:
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
results = face_mesh.process(rgb)

# ลด confidence threshold
face_mesh = mp.solutions.face_mesh.FaceMesh(
    min_detection_confidence=0.3,  # ลดจาก 0.5
    min_tracking_confidence=0.3
)
```

### Error 3: IndexError in Landmarks

```python
# ข้อผิดพลาด:
landmark = face_landmarks.landmark[500]  # IndexError!

# สาเหตุ: ใช้ index เกิน 467

# แก้: เช็คขนาดก่อน
if face_landmarks:
    num_landmarks = len(face_landmarks.landmark)
    print(f"Total landmarks: {num_landmarks}")  # 468
```

### Error 4: Meme Not Showing

```python
# สาเหตุ:
# 1. Path ผิด
# 2. ไฟล์เสีย
# 3. Alpha channel ไม่ถูกต้อง

# แก้: Add error checking
def load_meme_safe(path):
    if not os.path.exists(path):
        print(f"Meme not found: {path}")
        return None
    
    meme = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if meme is None:
        print(f"Failed to load: {path}")
        return None
    
    return meme
```

---

## 📊 Calibration & Tuning

### Finding Optimal Thresholds

```python
# สร้างโปรแกรมสำหรับ calibrate
import cv2
import mediapipe as mp

def calibration_tool():
    """แสดงค่า landmarks แบบ real-time"""
    cap = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        
        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            h, w = frame.shape[:2]
            
            # คำนวณค่าต่างๆ
            mouth_open = abs(lm[14].y - lm[13].y) * h
            eye_open = abs(lm[145].y - lm[159].y) * h
            brow_height = abs(lm[70].y - lm[159].y) * h
            
            # แสดงค่าบนหน้าจอ
            cv2.putText(frame, f"Mouth: {mouth_open:.1f}px", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.putText(frame, f"Eye: {eye_open:.1f}px", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.putText(frame, f"Brow: {brow_height:.1f}px", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        
        cv2.imshow("Calibration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# รัน และทดสอบท่าทางต่างๆ เพื่อหา threshold ที่เหมาะสม
calibration_tool()
```

---

## 🔗 External Resources

### MediaPipe Documentation
- Face Mesh: https://google.github.io/mediapipe/solutions/face_mesh.html
- Hands: https://google.github.io/mediapipe/solutions/hands.html
- Face Detection: https://google.github.io/mediapipe/solutions/face_detection.html

### OpenCV Documentation
- VideoCapture: https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
- Image Processing: https://docs.opencv.org/4.x/d2/d96/tutorial_py_table_of_contents_imgproc.html

### Python Libraries
- NumPy: https://numpy.org/doc/stable/
- Pillow: https://pillow.readthedocs.io/

---

**Last Updated**: 2026-07-05  
**Version**: 1.0

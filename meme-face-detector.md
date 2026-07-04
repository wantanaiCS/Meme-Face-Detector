# 🎭 Meme Face Detector

> ระบบตรวจจับลักษณะท่าทางและสีหน้าผ่านกล้อง แล้วแสดงภาพ Meme ตลก ๆ ตามท่าทางของคุณแบบ Real-time

---

## 📋 ภาพรวมโปรเจค

โปรเจคนี้ใช้ Python เป็นหลัก รวมเอาเทคโนโลยี Computer Vision มาวิเคราะห์ท่าทางผ่านกล้อง แล้วแสดง Meme ที่เหมาะสมกับสีหน้า/ท่าทางของผู้ใช้แบบ Real-time เมื่อท่าทางเปลี่ยน ภาพ Meme ก็จะเปลี่ยนตามทันที

---

## 🏗️ สถาปัตยกรรมระบบ

```
┌─────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────┐
│ กล้อง    │───▶│  OpenCV      │───▶│  MediaPipe /   │───▶│  Logic   │
│ Webcam  │    │  อ่าน Frame  │    │  FER วิเคราะห์ │    │  Map     │
└─────────┘    └──────────────┘    │  ใบหน้า+ท่าทาง  │    │  ท่าทาง  │
                                   └────────────────┘    └────┬─────┘
                                                              │
                                                              ▼
                                                        ┌──────────┐
                                                        │ เลือก    │
                                                        │ Meme     │
                                                        └────┬─────┘
                                                              │
                                                              ▼
┌─────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────┐
│ หน้าจอ  │◀───│  Pygame /    │◀───│  Pillow (PIL)  │◀───│ โฟลเดอร์ │
│ แสดงผล  │    │  OpenCV GUI  │    │  ปรับขนาดภาพ  │    │ memes/   │
└─────────┘    └──────────────┘    └────────────────┘    └──────────┘
```

### Flow การทำงาน

```
กล้องเปิด
    │
    ▼
อ่าน Frame จากกล้อง (OpenCV)
    │
    ▼
วิเคราะห์ Landmark ใบหน้า/มือ (MediaPipe)
    │
    ▼
คำนวณท่าทาง (ปากเปิด? ยิ้ม? ขมวดคิ้ว? ยกนิ้ว?)
    │
    ▼
Map ท่าทาง → เลือก Meme ที่เกี่ยวข้อง
    │
    ▼
แสดง Meme ซ้อนกับภาพกล้อง (Overlay)
    │
    ▼
วน Loop จนกว่าจะกดปิด (Q / ESC)
```

---

## 🛠️ Tech Stack

| ส่วน | เทคโนโลยี | เวอร์ชันแนะนำ | บทบาท |
|------|-----------|---------------|-------|
| ภาษา | Python | 3.8+ | ภาษาหลักของโปรเจค |
| กล้อง | OpenCV (`opencv-python`) | 4.8+ | เปิดกล้อง, อ่าน frame, ปรับขนาดภาพ, แสดงผล |
| ตรวจจับใบหน้า | MediaPipe (`mediapipe`) | 0.10+ | ตรวจจับ 468 จุด landmark บนใบหน้า, มือ 21 จุด |
| จำแนกอารมณ์ | FER (`fer`) | 2023+ | จำแนก 7 อารมณ์ (happy, sad, angry, surprise, fear, disgust, neutral) |
| จัดการภาพ | Pillow (`Pillow`) | 10+ | ปรับขนาด, วางซ้อน Meme ลงบนภาพกล้อง |
| แสดงผล | Pygame (`pygame`) | 2.5+ | หน้าต่าง GUI แสดงผลแบบ Real-time (ตัวเลือก) |
| OS | Windows / macOS / Linux | - | รองรับทุกระบบ |

---

## 📂 โครงสร้างโปรเจค

```
meme-face-detector/
│
├── main.py                  # 🚀 ไฟล์หลัก รัน entry point
├── requirements.txt         # 📦 รายการ dependencies
│
├── src/
│   ├── __init__.py
│   ├── camera.py            # 🎥 จัดการกล้อง (เปิด/ปิด/อ่าน frame)
│   ├── detector.py          # 🧠 ตรวจจับใบหน้า + ท่าทาง (MediaPipe + FER)
│   ├── expression_analyzer.py  # 📊 วิเคราะห์ landmark → ท่าทาง
│   ├── meme_selector.py     # 🖼️ Map ท่าทาง → เลือก Meme
│   ├── overlay.py           # 🔲 วางซ้อน Meme ลงบนภาพกล้อง
│   └── display.py           # 💻 แสดงผล GUI (OpenCV / Pygame)
│
├── memes/
│   ├── surprised/           # 😮 Meme สำหรับอารมณ์ประหลาดใจ
│   │   ├── surprised_pikachu.png
│   │   └── mind_blown.png
│   ├── happy/               # 😂 Meme สำหรับอารมณ์ยิ้ม/ขำ
│   │   ├── this_is_fine.png
│   │   └── laughing_cat.png
│   ├── angry/               # 😠 Meme สำหรับอารมณ์โกรธ
│   │   ├── angry_cat.png
│   │   └── rage_face.png
│   ├── sleepy/              # 😴 Meme สำหรับอารมณ์เบื่อ/ง่วง
│   │   ├── bored_ape.png
│   │   └── sleepy_panda.png
│   ├── thinking/            # 🤔 Meme สำหรับอารมณ์คิด/สงสัย
│   │   ├── thinking_face.png
│   │   └── math_lady.png
│   ├── thumbs_up/           # 👍 Meme สำหรับท่าทางยกนิ้วโป้ง
│   │   └── thumbs_up_kid.png
│   ├── peace/               # ✌️ Meme สำหรับท่าทางยกนิ้วสอง
│   │   └── peace_victory.png
│   └── neutral/             # 😐 Meme สำหรับใบหน้าเฉยๆ
│       ├── stonks.png
│       └── drake_hotline.png
│
├── config/
│   ├── expression_rules.json  # กฎการตีความท่าทาง (threshold)
│   └── meme_mapping.json      # Map ท่าทาง → ชื่อโฟลเดอร์ Meme
│
└── assets/
    └── fonts/               # ฟอนต์สำหรับแสดงข้อความบนภาพ (ถ้าต้องการ)
```

---

## 🚀 การติดตั้ง

### ข้อกำหนดระบบ

| สิ่งที่ต้องมี | รายละเอียด |
|--------------|-----------|
| Python | 3.8 ขึ้นไป |
| กล้อง | Webcam USB หรือ Built-in Camera |
| RAM | 4GB ขึ้นไป |
| GPU | ไม่จำเป็น (MediaPipe ทำงานบน CPU ได้เต็มรูปแบบ) |
| OS | Windows / macOS / Linux |

### สร้าง Virtual Environment

```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### ติดตั้ง Dependencies

```bash
pip install opencv-python mediapipe fer Pillow pygame numpy
```

### สร้างไฟล์ requirements.txt

```text
opencv-python>=4.8.0
mediapipe>=0.10.0
fer>=2023.0.0
Pillow>=10.0.0
pygame>=2.5.0
numpy>=1.24.0
```

ติดตั้งจาก requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 🧠 รายละเอียดการตรวจจับ

### 1. MediaPipe Face Mesh — จุด Landmark สำคัญ

MediaPipe ตรวจจับใบหน้าได้ **468 จุด landmark** บนใบหน้า จุดสำคัญที่ใช้วิเคราะห์ท่าทาง:

```
จุดสำคัญบนใบหน้า MediaPipe:

ริมฝีปาก:
  - ปากบน: ลำดับ 13 (กลางริมฝีปากบน)
  - ปากล่าง: ลำดับ 14 (กลางริมฝีปากล่าง)
  - มุมปากซ้าย: ลำดับ 61
  - มุมปากขวา: ลำดับ 291

คิ้ว:
  - คิ้วซ้าย: ลำดับ 70, 63, 105, 66, 107
  - คิ้วขวา: ลำดับ 336, 296, 334, 293, 300

ตา:
  - ตาขวาบน: ลำดับ 159
  - ตาขวาล่าง: ลำดับ 145
  - ตาซ้ายบน: ลำดับ 386
  - ตาซ้ายล่าง: ลำดับ 374

จมูก:
  - ปลายจมูก: ลำดับ 1
```

### 2. กฎการตีความท่าทาง (Expression Rules)

```json
{
  "rules": {
    "surprised": {
      "description": "ปากเปิดกว้าง + คิ้วยกสูง",
      "conditions": {
        "mouth_open": { "min": 25, "unit": "pixels" },
        "brow_raise": { "min": 0.02, "unit": "ratio" }
      }
    },
    "happy": {
      "description": "ยิ้ม — มุมปากยกขึ้น + ปากเปิดเล็กน้อย",
      "conditions": {
        "mouth_corner_raise": { "min": 0.015, "unit": "ratio" },
        "mouth_open": { "min": 5, "max": 20, "unit": "pixels" }
      }
    },
    "angry": {
      "description": "โกรธ — คิ้วขมวดลง + ริมฝีปากแน่น",
      "conditions": {
        "brow_furrow": { "min": 0.015, "unit": "ratio" },
        "mouth_open": { "max": 8, "unit": "pixels" }
      }
    },
    "sleepy": {
      "description": "ง่วง/เบื่อ — ตาหลับเกือบสนิท",
      "conditions": {
        "eye_open": { "max": 5, "unit": "pixels" }
      }
    },
    "thinking": {
      "description": "คิด/สงสัย — เอียงหัวหรือมุมปากข้างหนึ่งยก",
      "conditions": {
        "head_tilt": { "min": 5, "unit": "degrees" }
      }
    }
  }
}
```

### 3. MediaPipe Hands — ตรวจจับท่าทางมือ

```
จุด Landmark มือ MediaPipe (21 จุด):

     8──9──10──11──12
    /               \
   7                 13
   |                 |
   6                 14
   |                 |
   5                 15
    \               /
 4──3──2──1──0──16──17──18──19──20
    (wrist)       (palm)

นิ้วโป้ง (Thumb):    1, 2, 3, 4
นิ้วชี้ (Index):     5, 6, 7, 8
นิ้วกลาง (Middle):   9, 10, 11, 12
นิ้วนาง (Ring):      13, 14, 15, 16
นิ้วก้อย (Pinky):    17, 18, 19, 20
```

ท่าทางมือที่รองรับ:

| ท่าทาง | วิธีตรวจจับ | Meme |
|--------|------------|------|
| ยกนิ้วโป้ง | ปลายนิ้วโป้ง (4) สูงกว่า IP joint (3) | Thumbs Up Kid |
| ยกนิ้วสอง (V) | ปลายนิ้วชี้ (8) + นิ้วกลาง (12) ยื่น, นิ้วอื่นพับ | Peace Victory |
| ยกนิ้วชี้ | เฉพาะนิ้วชี้ (8) ยื่น | Wait What |
| กำปั้น | ทุกนิ้วพับ | Fist Bump |

---

## 🗺️ Meme Mapping

### ตาราง Map ท่าทาง → Meme

| ท่าทาง | โฟลเดอร์ | ไฟล์ Meme | คำอธิบาย |
|--------|---------|-----------|----------|
| 😮 ประหลาดใจ | `memes/surprised/` | surprised_pikachu.png | Pikachu ประหลาดใจ |
| 😮 ประหลาดใจ | `memes/surprised/` | mind_blown.png | หัวระเบิด |
| 😂 ยิ้ม/ขำ | `memes/happy/` | this_is_fine.png | สุนัขนั่งในไฟ "This is Fine" |
| 😂 ยิ้ม/ขำ | `memes/happy/` | laughing_cat.png | แมวขำ |
| 😠 โกรธ | `memes/angry/` | angry_cat.png | แมวโกรธ |
| 😠 โกรธ | `memes/angry/` | rage_face.png | หน้าโกรธสุด |
| 😴 ง่วง/เบื่อ | `memes/sleepy/` | bored_ape.png | Bored Ape |
| 😴 ง่วง/เบื่อ | `memes/sleepy/` | sleepy_panda.png | หมีแพนด้าง่วง |
| 🤔 คิด/สงสัย | `memes/thinking/` | thinking_face.png | หน้าคิด |
| 🤔 คิด/สงสัย | `memes/thinking/` | math_lady.png | สาวนักคณิตศาสตร์ |
| 👍 ยกนิ้วโป้ง | `memes/thumbs_up/` | thumbs_up_kid.png | เด็กยกนิ้วโป้ง |
| ✌️ ยกนิ้วสอง | `memes/peace/` | peace_victory.png | แสดง V |
| 😐 เฉยๆ | `memes/neutral/` | stonks.png | Stonks Man |
| 😐 เฉยๆ | `memes/neutral/` | drake_hotline.png | Drake Bling |

---

## 💻 โค้ดตัวอย่าง

### main.py — Entry Point

```python
import cv2
from src.camera import Camera
from src.detector import FaceDetector
from src.expression_analyzer import ExpressionAnalyzer
from src.meme_selector import MemeSelector
from src.overlay import MemeOverlay
from src.display import Display

def main():
    # เริ่มต้นส่วนประกอบทั้งหมด
    camera = Camera(camera_id=0)
    detector = FaceDetector()
    analyzer = ExpressionAnalyzer()
    meme_selector = MemeSelector(meme_dir="memes/")
    overlay = MemeOverlay()
    display = Display(window_name="Meme Face Detector")

    print("🎬 เริ่ม Meme Face Detector")
    print("กด 'Q' หรือ 'ESC' เพื่อออก")

    try:
        while True:
            # 1. อ่านภาพจากกล้อง
            frame = camera.read_frame()
            if frame is None:
                break

            # 2. ตรวจจับใบหน้า
            face_landmarks = detector.detect_faces(frame)
            hand_landmarks = detector.detect_hands(frame)

            # 3. วิเคราะห์ท่าทาง
            expression = analyzer.analyze_expression(face_landmarks, frame.shape)
            gesture = analyzer.analyze_gesture(hand_landmarks, frame.shape)

            # 4. เลือก Meme (ท่าทางมือมี priority สูงกว่าสีหน้า)
            current_state = gesture if gesture else expression
            meme_path = meme_selector.select_meme(current_state)

            # 5. วางซ้อน Meme ลงบนภาพกล้อง
            if meme_path:
                frame = overlay.apply(frame, meme_path, position="top_right")

            # 6. แสดงผล
            display.show(frame)
            if display.should_exit():
                break

    finally:
        camera.release()
        display.close()

if __name__ == "__main__":
    main()
```

### camera.py — จัดการกล้อง

```python
import cv2

class Camera:
    def __init__(self, camera_id=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        # กลับภาพซ้าย-ขวา (mirror)
        return cv2.flip(frame, 1)

    def release(self):
        self.cap.release()
```

### detector.py — ตรวจจับใบหน้าและมือ

```python
import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def detect_faces(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        return None

    def detect_hands(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if results.multi_hand_landmarks:
            return results.multi_hand_landmarks[0]
        return None
```

### expression_analyzer.py — วิเคราะห์ท่าทาง

```python
import numpy as np

class ExpressionAnalyzer:
    def analyze_expression(self, face_landmarks, frame_shape):
        """
        วิเคราะห์ท่าทางใบหน้าจาก landmark 468 จุด
        คืนค่า: str ชื่อท่าทาง เช่น "surprised", "happy", "angry" ฯลฯ
        """
        if face_landmarks is None:
            return "neutral"

        h, w, _ = frame_shape
        lm = face_landmarks.landmark

        # คำนวณค่าต่างๆ
        mouth_open = abs(lm[14].y - lm[13].y) * h
        mouth_width = abs(lm[291].x - lm[61].x) * w
        mouth_corner_raise = min(lm[61].y, lm[291].y) - lm[13].y
        eye_open = abs(lm[145].y - lm[159].y) * h
        brow_raise = abs(lm[70].y - lm[159].y) * h
        head_tilt = abs(lm[1].x - 0.5) * w

        # ตรวจสอบท่าทางตามกฎ (priority จากบนลงล่าง)
        if mouth_open > 25 and brow_raise > 15:
            return "surprised"
        elif eye_open < 5:
            return "sleepy"
        elif mouth_open > 10 and mouth_corner_raise < -0.01:
            return "happy"
        elif brow_raise < 8 and mouth_open < 8:
            return "angry"
        elif head_tilt > 30:
            return "thinking"
        else:
            return "neutral"

    def analyze_gesture(self, hand_landmarks, frame_shape):
        """
        วิเคราะห์ท่าทางมือจาก landmark 21 จุด
        คืนค่า: str ชื่อท่าทาง เช่น "thumbs_up", "peace" ฯลฯ
        """
        if hand_landmarks is None:
            return None

        lm = hand_landmarks.landmark

        # ตรวจจับยกนิ้วโป้ง
        thumb_up = lm[4].y < lm[3].y and lm[3].y < lm[2].y

        # ตรวจจับนิ้วแต่ละนิ้วยื่นหรือพับ
        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up = lm[16].y < lm[14].y
        pinky_up = lm[20].y < lm[18].y

        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "thumbs_up"
        elif index_up and middle_up and not ring_up and not pinky_up:
            return "peace"
        elif index_up and not middle_up and not ring_up and not pinky_up:
            return "pointing"
        elif not index_up and not middle_up and not ring_up and not pinky_up:
            return "fist"
        else:
            return None
```

### meme_selector.py — เลือก Meme

```python
import os
import random

class MemeSelector:
    def __init__(self, meme_dir="memes/"):
        self.meme_dir = meme_dir
        self.mapping = {
            "surprised": "surprised/",
            "happy": "happy/",
            "angry": "angry/",
            "sleepy": "sleepy/",
            "thinking": "thinking/",
            "thumbs_up": "thumbs_up/",
            "peace": "peace/",
            "neutral": "neutral/",
        }
        self.last_meme = None
        self.cooldown = 0  # ป้องกันเปลี่ยน Meme บ่อยเกินไป

    def select_meme(self, expression):
        """
        เลือก Meme จากท่าทางที่ตรวจจับได้
        คืนค่า: path ของไฟล์ Meme หรือ None
        """
        folder_name = self.mapping.get(expression, "neutral/")
        folder_path = os.path.join(self.meme_dir, folder_name)

        if not os.path.isdir(folder_path):
            return None

        memes = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]

        if not memes:
            return None

        # หลีกเลี่ยงเลือก Meme เดิม 2 รอบติดต่อกัน
        if len(memes) > 1:
            memes = [m for m in memes if m != self.last_meme]

        selected = random.choice(memes)
        self.last_meme = selected
        return selected
```

### overlay.py — วางซ้อน Meme บนภาพ

```python
import cv2
import numpy as np

class MemeOverlay:
    def apply(self, frame, meme_path, position="top_right", size=(250, 250)):
        """
        วางซ้อนภาพ Meme ลงบน frame ของกล้อง
        """
        meme = cv2.imread(meme_path, cv2.IMREAD_UNCHANGED)
        if meme is None:
            return frame

        # ปรับขนาด Meme
        meme = cv2.resize(meme, size, interpolation=cv2.INTER_AREA)

        # หาตำแหน่งวาง
        h, w = meme.shape[:2]
        fh, fw = frame.shape[:2]

        positions = {
            "top_left": (10, 10),
            "top_right": (fw - w - 10, 10),
            "bottom_left": (10, fh - h - 10),
            "bottom_right": (fw - w - 10, fh - h - 10),
        }

        x, y = positions.get(position, positions["top_right"])

        # วางภาพโปร่งใส (RGBA)
        if meme.shape[2] == 4:
            alpha = meme[:, :, 3] / 255.0
            for c in range(3):
                frame[y:y+h, x:x+w, c] = (
                    alpha * meme[:, :, c] + (1 - alpha) * frame[y:y+h, x:x+w, c]
                )
        else:
            frame[y:y+h, x:x+w] = meme

        return frame
```

### display.py — แสดงผล

```python
import cv2

class Display:
    def __init__(self, window_name="Meme Face Detector"):
        self.window_name = window_name

    def show(self, frame):
        cv2.imshow(self.window_name, frame)

    def should_exit(self):
        key = cv2.waitKey(1) & 0xFF
        return key in (ord('q'), ord('Q'), 27)  # Q หรือ ESC

    def close(self):
        cv2.destroyAllWindows()
```

---

## 🚀 วิธีรันโปรแกรม

```bash
# 1. เข้าไปในโฟลเดอร์โปรเจค
cd meme-face-detector

# 2. เปิด virtual environment
source venv/bin/activate      # macOS/Linux
# หรือ
venv\Scripts\activate         # Windows

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. รันโปรเจค
python main.py

# 5. กด Q หรือ ESC เพื่อออก
```

---

## 🔧 การปรับแต่ง

### เพิ่ม Meme ใหม่

1. เตรียมภาพ Meme (PNG แบบโปร่งใสจะดีที่สุด)
2. ใส่ลงในโฟลเดอร์ที่เหมาะสม เช่น `memes/happy/my_meme.png`
3. โปรแกรมจะโหลด Meme ใหม่อัตโนมัติ

### ปรับความไวในการตรวจจับ

แก้ไขค่า threshold ใน `expression_analyzer.py`:

```python
# ปากเปิดกว้างแค่ไหนถึงจะถือว่า "surprised"
if mouth_open > 25:     # ลดค่า = ไวขึ้น, เพิ่มค่า = ช้าขึ้น
    return "surprised"

# ตาหลับแค่ไหนถึงจะถือว่า "sleepy"
if eye_open < 5:        # เพิ่มค่า = ไวขึ้น, ลดค่า = ช้าขึ้น
    return "sleepy"
```

### เปลี่ยนตำแหน่ง/ขนาด Meme

ใน `main.py` แก้พารามิเตอร์ของ `MemeOverlay`:

```python
overlay = MemeOverlay()

# ปรับขนาด Meme (กว้าง, สูง)
frame = overlay.apply(frame, meme_path, size=(300, 300))

# เปลี่ยนตำแหน่ง: "top_left", "top_right", "bottom_left", "bottom_right"
frame = overlay.apply(frame, meme_path, position="bottom_right")
```

---

## 🐛 การแก้ไขปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|--------|
| กล้องไม่เปิด | กล้องถูกโปรแกรมอื่นใช้งานอยู่ | ปิดโปรแกรมอื่นที่ใช้กล้อง หรือเปลี่ยน `camera_id=0` เป็น `1` |
| ตรวจจับไม่แม่น | แสงน้อยเกินไป | เพิ่มแสงในห้อง หรือปรับ `min_detection_confidence` |
| Meme ไม่แสดง | ไม่มีไฟล์ภาพในโฟลเดอร์ | ใส่ภาพ PNG/JPG ลงในโฟลเดอร์ `memes/` ตามหมวดหมู่ |
| โปรแกรมช้า | ความละเอียดกล้องสูงเกินไป | ลดความละเอียดใน `Camera()` เช่น `width=640, height=480` |
| MediaPipe โหลดช้า | ต้องโหลดโมเดลครั้งแรก | รอสักครู่ครั้งแรก ครั้งต่อไปจะเร็วขึ้น |
| FER import ไม่ได้ | ขาด dependency | `pip install fer tensorflow` |

---

## 📈 ไอเดียพัฒนาต่อยอด

- **เพิ่ม Sound Effect** — เล่นเสียงตลกตาม Meme ที่แสดง (ใช้ `pygame.mixer`)
- **บันทึกคลิป** — บันทึกวิดีโอพร้อม Meme overlay (ใช้ `cv2.VideoWriter`)
- **Screenshot** กดปุ่มเพื่อถ่ายภาพ Meme ที่แสดงอยู่
- **AI สร้าง Meme** — ใช้ AI สร้างข้อความ Meme แบบ Dynamic ตามท่าทาง
- **Web Version** — ใช้ FastAPI + WebSocket ส่งภาพไปแสดงบนเบราว์เซอร์
- **Multi-face** — รองรับหลายคนพร้อมกัน แต่ละคนแสดง Meme ต่างกัน
- **Face Filter** — เพิ่ม Effect ซ้อนบนใบหน้า (หูแมว, แว่น, หมวก) เหมือน Snapchat
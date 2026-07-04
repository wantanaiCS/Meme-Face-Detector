---
inclusion: auto
---

# 📐 Initial — โครงสร้างโปรเจคและแผนการพัฒนา

> เอกสารนี้เป็นจุดเริ่มต้นของโปรเจค Meme Face Detector กำหนดโครงสร้างไฟล์และลำดับการพัฒนา

---

## 🎯 Project Overview

**Meme Face Detector** คือระบบตรวจจับใบหน้าและท่าทางผ่านกล้อง แล้วแสดง Meme ที่เหมาะสมแบบ Real-time

**เทคโนโลジีหลัก**:
- Python 3.8+
- OpenCV (กล้อง + แสดงผล)
- MediaPipe (ตรวจจับใบหน้า/มือ)
- NumPy (คำนวณ)

---

## 📂 โครงสร้างไฟล์แบบสมบูรณ์

```
meme-face-detector/
│
├── .git/                           # Git repository
├── .gitignore                      # Git ignore patterns
│
├── .kiro/                          # Kiro IDE configuration
│   ├── steering/
│   │   ├── generate-prp.md         # 🎯 Project Requirements & Patterns
│   │   └── Initial.md              # 📐 โครงสร้างโปรเจคและแผน (ไฟล์นี้)
│   └── hooks/                      # Agent hooks (ถ้ามี)
│
├── main.py                         # 🚀 Entry point หลัก
├── requirements.txt                # 📦 Python dependencies
├── README.md                       # 📖 เอกสารโปรเจค
├── .env.example                    # ตัวอย่างไฟล์ environment variables
│
├── src/                            # 📁 Source code หลัก
│   ├── __init__.py
│   ├── camera.py                   # 🎥 Camera input manager
│   ├── detector.py                 # 🧠 Face/Hand detection (MediaPipe)
│   ├── expression_analyzer.py      # 📊 Expression analysis logic
│   ├── meme_selector.py            # 🖼️ Meme selection engine
│   ├── overlay.py                  # 🔲 Image overlay renderer
│   └── display.py                  # 💻 Display manager (OpenCV/Pygame)
│
├── config/                         # ⚙️ Configuration files
│   ├── expression_rules.json       # กฎการวิเคราะห์ท่าทาง
│   └── meme_mapping.json           # แมปท่าทาง → Meme folder
│
├── memes/                          # 🖼️ Meme images repository
│   ├── surprised/                  # 😮 Surprised memes
│   │   ├── surprised_pikachu.png
│   │   └── mind_blown.png
│   ├── happy/                      # 😂 Happy memes
│   │   ├── this_is_fine.png
│   │   └── laughing_cat.png
│   ├── angry/                      # 😠 Angry memes
│   │   ├── angry_cat.png
│   │   └── rage_face.png
│   ├── sleepy/                     # 😴 Sleepy/bored memes
│   │   ├── bored_ape.png
│   │   └── sleepy_panda.png
│   ├── thinking/                   # 🤔 Thinking memes
│   │   ├── thinking_face.png
│   │   └── math_lady.png
│   ├── thumbs_up/                  # 👍 Thumbs up memes
│   │   └── thumbs_up_kid.png
│   ├── peace/                      # ✌️ Peace sign memes
│   │   └── peace_victory.png
│   └── neutral/                    # 😐 Neutral memes
│       ├── stonks.png
│       └── drake_hotline.png
│
├── assets/                         # 🎨 Additional assets
│   └── fonts/                      # Font files (optional)
│       └── arial.ttf
│
├── tests/                          # 🧪 Unit tests (optional)
│   ├── __init__.py
│   ├── test_camera.py
│   ├── test_detector.py
│   └── test_analyzer.py
│
├── docs/                           # 📚 Additional documentation
│   ├── mediapipe_landmarks.md      # MediaPipe landmark reference
│   ├── expression_logic.md         # การคำนวณท่าทาง
│   └── adding_memes.md             # คู่มือเพิ่ม Meme
│
└── examples/                       # 💡 Example scripts
    ├── test_camera.py              # ทดสอบกล้อง
    ├── test_face_detection.py      # ทดสอบตรวจจับใบหน้า
    └── test_hand_detection.py      # ทดสอบตรวจจับมือ
```

---

## 🗂️ รายละเอียดแต่ละโฟลเดอร์

### `src/` — Source Code
โค้ดหลักทั้งหมด แบ่งเป็น 6 โมดูลใหญ่

| ไฟล์ | Class | หน้าที่ |
|------|-------|---------|
| `camera.py` | `Camera` | เปิด/ปิดกล้อง, อ่าน frame |
| `detector.py` | `FaceDetector` | ตรวจจับใบหน้า/มือด้วย MediaPipe |
| `expression_analyzer.py` | `ExpressionAnalyzer` | วิเคราะห์ท่าทางจาก landmarks |
| `meme_selector.py` | `MemeSelector` | เลือก Meme ตามท่าทาง |
| `overlay.py` | `MemeOverlay` | วางซ้อน Meme บนภาพกล้อง |
| `display.py` | `Display` | แสดงผลหน้าจอ + จัดการ keyboard |

### `config/` — Configuration
ไฟล์ config แบบ JSON ควบคุมพฤติกรรมโปรแกรม

**expression_rules.json**: กำหนดกฎการตีความท่าทาง
```json
{
  "surprised": {
    "mouth_open_threshold": 25,
    "brow_raise_threshold": 15
  },
  "happy": {
    "mouth_corner_raise_threshold": 0.015,
    "mouth_open_min": 5,
    "mouth_open_max": 20
  }
}
```

**meme_mapping.json**: แมปท่าทาง → โฟลเดอร์ Meme
```json
{
  "surprised": "surprised",
  "happy": "happy",
  "angry": "angry",
  "sleepy": "sleepy",
  "thinking": "thinking",
  "thumbs_up": "thumbs_up",
  "peace": "peace",
  "neutral": "neutral"
}
```

### `memes/` — Meme Repository
เก็บภาพ Meme แบ่งตามหมวดหมู่

**รูปแบบไฟล์**:
- PNG (แนะนำ — รองรับโปร่งใส)
- JPG/JPEG (ใช้ได้)
- GIF (static frame เท่านั้น)

**ขนาดแนะนำ**: 300x300 ถึง 500x500 pixels

### `tests/` — Unit Tests (Optional)
ไฟล์ทดสอบแต่ละโมดูล (ถ้าต้องการ)

### `docs/` — Documentation
เอกสารอ้างอิงเพิ่มเติม

### `examples/` — Example Scripts
โค้ดตัวอย่างเพื่อทดสอบแต่ละส่วน

---

## 🚀 Development Roadmap

### ✅ Phase 0: Project Setup
**เป้าหมาย**: เตรียมโครงสร้างโปรเจค

**Tasks**:
- [x] สร้างโครงสร้างโฟลเดอร์
- [x] สร้าง generate-prp.md และ Initial.md
- [ ] สร้าง requirements.txt
- [ ] สร้าง .gitignore
- [ ] สร้าง README.md เบื้องต้น
- [ ] ตั้งค่า virtual environment

**ผลลัพธ์**: โครงสร้างโปรเจคพร้อมใช้งาน

---

### 🔧 Phase 1: Core Infrastructure
**เป้าหมาย**: สร้างโครงสร้างพื้นฐานของระบบ

**Tasks**:
- [ ] สร้าง `src/camera.py` (Camera class)
  - เปิด/ปิดกล้อง
  - อ่าน frame
  - Mirror image
  - Error handling
- [ ] สร้าง `src/display.py` (Display class)
  - แสดงภาพด้วย OpenCV
  - ตรวจจับ keyboard (Q/ESC)
- [ ] สร้าง `main.py` เวอร์ชันเบื้องต้น
  - เปิดกล้อง → แสดงผล → ปิดกล้อง
- [ ] ทดสอบ: กล้องเปิด/แสดงผลได้

**ผลลัพธ์**: โปรแกรมแสดงภาพจากกล้อง Real-time

---

### 🧠 Phase 2: Face Detection
**เป้าหมาย**: เพิ่มระบบตรวจจับใบหน้า

**Tasks**:
- [ ] สร้าง `src/detector.py` (FaceDetector class)
  - Initialize MediaPipe Face Mesh
  - detect_faces() method
  - แปลง BGR → RGB
- [ ] วาด landmarks ลงบนภาพ (เพื่อ debug)
- [ ] แสดง FPS บนหน้าจอ
- [ ] ทดสอบ: ตรวจจับใบหน้าได้แม่นยำ

**ผลลัพธ์**: เห็นจุด landmarks บนใบหน้า

---

### 📊 Phase 3: Expression Analysis
**เป้าหมาย**: วิเคราะห์ท่าทางจาก landmarks

**Tasks**:
- [ ] สร้าง `src/expression_analyzer.py` (ExpressionAnalyzer class)
- [ ] สร้างฟังก์ชันคำนวณ:
  - `_calculate_mouth_open()`
  - `_calculate_eye_open()`
  - `_calculate_brow_raise()`
  - `_calculate_mouth_corner_raise()`
- [ ] สร้าง `analyze_expression()` — ตรรกะตัดสินใจท่าทาง
- [ ] สร้าง `config/expression_rules.json`
- [ ] แสดงชื่อท่าทางที่ตรวจจับได้บนหน้าจอ
- [ ] ทดสอบ: ทุกท่าทางแยกแยะได้ถูกต้อง

**ผลลัพธ์**: โปรแกรมบอกได้ว่าท่าทางคืออะไร

---

### 🖼️ Phase 4: Meme Integration
**เป้าหมาย**: เพิ่มระบบแสดง Meme

**Tasks**:
- [ ] สร้าง `src/meme_selector.py` (MemeSelector class)
  - โหลดรายชื่อ Meme จาก memes/
  - `select_meme(expression)` — เลือก Meme
  - Random selection + avoid repeat
- [ ] สร้าง `src/overlay.py` (MemeOverlay class)
  - โหลดภาพ Meme
  - ปรับขนาด
  - วางซ้อนบนภาพกล้อง (รองรับ alpha channel)
- [ ] สร้าง `config/meme_mapping.json`
- [ ] เพิ่มภาพ Meme ตัวอย่างลงในโฟลเดอร์ memes/
- [ ] ทดสอบ: Meme แสดงผลถูกต้อง

**ผลลัพธ์**: เมื่อเปลี่ยนท่าทาง Meme จะเปลี่ยนตาม

---

### 🖐️ Phase 5: Hand Gesture (Optional)
**เป้าหมาย**: เพิ่มการตรวจจับท่าทางมือ

**Tasks**:
- [ ] เพิ่ม `detect_hands()` ใน `detector.py`
- [ ] เพิ่ม `analyze_gesture()` ใน `expression_analyzer.py`
  - ตรวจจับยกนิ้วโป้ง
  - ตรวจจับ V sign
  - ตรวจจับกำปั้น
- [ ] Priority: ท่าทางมือ > สีหน้า
- [ ] เพิ่ม Meme สำหรับท่าทางมือ
- [ ] ทดสอบ: ท่าทางมือใช้งานได้

**ผลลัพธ์**: ยกนิ้วโป้ง/V sign แสดง Meme พิเศษ

---

### ✨ Phase 6: Polish & Optimization
**เป้าหมาย**: ปรับปรุงประสิทธิภาพและประสบการณ์ผู้ใช้

**Tasks**:
- [ ] ปรับแต่ง threshold ให้ตรวจจับแม่นขึ้น
- [ ] เพิ่ม smoothing — ป้องกัน Meme เปลี่ยนบ่อยเกินไป
- [ ] เพิ่ม cooldown timer
- [ ] เพิ่มตัวเลือก command-line arguments:
  - `--camera-id` เลือกกล้อง
  - `--resolution` ความละเอียด
  - `--meme-size` ขนาด Meme
  - `--position` ตำแหน่ง Meme
- [ ] Error handling ทุกส่วน
- [ ] Performance profiling
- [ ] เขียน README.md แบบสมบูรณ์
- [ ] เขียน docstrings ครบทุก class/function

**ผลลัพธ์**: โปรแกรมพร้อมใช้งานจริง

---

### 🎁 Phase 7: Extra Features (Optional)
**เป้าหมาย**: ฟีเจอร์เสริมตามความต้องการ

**Possible Features**:
- [ ] บันทึกวิดีโอพร้อม Meme overlay
- [ ] Screenshot — กดปุ่มถ่ายภาพ
- [ ] Sound effects ตาม Meme
- [ ] Web version (FastAPI + WebSocket)
- [ ] Multi-face support
- [ ] Face filters/effects
- [ ] Custom Meme creator

---

## 📋 Initial Files to Create

### 1. requirements.txt
```text
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
Pillow>=10.0.0
```

### 2. .gitignore
```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.mp4
*.avi
screenshots/
```

### 3. README.md (ใช้จาก meme-face-detector.md)

### 4. Config Files

**config/expression_rules.json**:
```json
{
  "surprised": {
    "mouth_open_threshold": 25,
    "brow_raise_threshold": 15
  },
  "happy": {
    "mouth_corner_raise_min": 0.015,
    "mouth_open_min": 5,
    "mouth_open_max": 20
  },
  "angry": {
    "brow_furrow_threshold": 0.015,
    "mouth_open_max": 8
  },
  "sleepy": {
    "eye_open_max": 5
  },
  "thinking": {
    "head_tilt_min": 5
  }
}
```

**config/meme_mapping.json**:
```json
{
  "surprised": "surprised",
  "happy": "happy",
  "angry": "angry",
  "sleepy": "sleepy",
  "thinking": "thinking",
  "thumbs_up": "thumbs_up",
  "peace": "peace",
  "neutral": "neutral"
}
```

---

## 🎯 Success Criteria

โปรเจคสำเร็จเมื่อ:
- ✅ กล้องเปิดและแสดงผลได้ Real-time (30 FPS+)
- ✅ ตรวจจับใบหน้าได้แม่นยำในสภาพแสงปกติ
- ✅ แยกแยะท่าทางได้อย่างน้อย 5 แบบ (surprised, happy, angry, sleepy, neutral)
- ✅ แสดง Meme ที่เหมาะสมตามท่าทาง
- ✅ Meme เปลี่ยนทันทีเมื่อท่าทางเปลี่ยน
- ✅ โปรแกรมไม่ crash และปิดได้ด้วย Q/ESC
- ✅ โค้ดเป็นโมดูลและแยกหน้าที่ชัดเจน
- ✅ มี error handling ที่เหมาะสม
- ✅ มีเอกสารครบถ้วน

---

## 🔗 Related Documents

- **generate-prp.md** — Project Requirements & Patterns
- **meme-face-detector.md** — รายละเอียดทางเทคนิคแบบเต็ม
- **README.md** — เอกสารสำหรับผู้ใช้

---

## 📝 Notes

### ทำไมต้องแยกเป็นโมดูล?
1. **Maintainability** — แก้ไขง่าย ไม่กระทบส่วนอื่น
2. **Testability** — ทดสอบทีละส่วนได้
3. **Reusability** — เอาโมดูลไปใช้ในโปรเจคอื่นได้
4. **Collaboration** — หลายคนทำงานร่วมกันได้
5. **AI-Friendly** — AI agent เข้าใจ context ได้ง่ายขึ้น

### การใช้ Config Files
ไฟล์ JSON แยก config จากโค้ด = ปรับแต่งได้โดยไม่ต้องแก้โค้ด

### Meme Organization
แยกโฟลเดอร์ตามหมวดหมู่ = เพิ่ม Meme ใหม่ง่าย โปรแกรมโหลดอัตโนมัติ

---

**Last Updated**: 2026-07-05  
**Version**: 1.0  
**Status**: ✅ Ready for Development

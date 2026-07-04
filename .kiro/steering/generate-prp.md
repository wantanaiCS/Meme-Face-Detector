---
inclusion: auto
---

# 🎯 Generate PRP (Project Requirements & Patterns)

> เอกสารนี้กำหนด Prompt Engineering Patterns และแนวทางการพัฒนาโปรเจค Meme Face Detector

---

## 📋 Project Context

**ชื่อโปรเจค**: Meme Face Detector  
**ประเภท**: Computer Vision + Real-time Interactive Application  
**ภาษาหลัก**: Python 3.8+  
**จุดประสงค์**: ตรวจจับใบหน้าและท่าทางผ่านกล้อง แล้วแสดง Meme ที่เหมาะสมแบบ Real-time

---

## 🏗️ Architecture Patterns

### 1. Modular Design Pattern
```
โครงสร้างโค้ดแบ่งเป็นโมดูลอิสระ:
- Camera Module: จัดการอินพุตจากกล้อง
- Detector Module: ตรวจจับใบหน้าและมือ
- Analyzer Module: วิเคราะห์ท่าทางจาก landmarks
- Selector Module: เลือก Meme ที่เหมาะสม
- Overlay Module: วางซ้อนภาพ
- Display Module: แสดงผลออกหน้าจอ
```

### 2. Pipeline Processing Pattern
```
Camera → Detector → Analyzer → Selector → Overlay → Display
```

### 3. Configuration-Driven Pattern
```
ใช้ไฟล์ JSON config แยกจากโค้ด:
- expression_rules.json: กฎการวิเคราะห์ท่าทาง
- meme_mapping.json: แมปท่าทาง → โฟลเดอร์ Meme
```

---

## 🎨 Code Style Guidelines

### Python Style
- ใช้ **PEP 8** style guide
- ชื่อ class: `PascalCase` (เช่น `FaceDetector`)
- ชื่อ function/variable: `snake_case` (เช่น `detect_faces`)
- ชื่อ constant: `UPPER_SNAKE_CASE` (เช่น `MAX_NUM_FACES`)
- Docstring: ใช้ Google style หรือ NumPy style

### File Organization
```
src/
  ├── __init__.py           # Package marker
  ├── camera.py             # Class: Camera
  ├── detector.py           # Class: FaceDetector
  ├── expression_analyzer.py # Class: ExpressionAnalyzer
  ├── meme_selector.py      # Class: MemeSelector
  ├── overlay.py            # Class: MemeOverlay
  └── display.py            # Class: Display
```

### Import Order
1. Standard library (os, sys, json)
2. Third-party (cv2, mediapipe, numpy)
3. Local modules (src.*)

---

## 🧠 AI Development Instructions

### เมื่อเขียนโค้ดใหม่
1. **อ่านไฟล์ที่เกี่ยวข้องก่อน** — เช็ค pattern ที่มีอยู่
2. **สร้าง class ที่ single responsibility** — ทำหน้าที่เดียวให้ดี
3. **เขียน type hints** — ระบุ type ของพารามิเตอร์และ return value
4. **เพิ่ม error handling** — ใช้ try-except สำหรับการเปิดกล้อง, โหลดไฟล์, อ่านภาพ
5. **ทดสอบทีละโมดูล** — ก่อนรวมเข้า pipeline หลัก

### เมื่อแก้ไขโค้ด
1. **เช็ค dependencies** — ดูว่าการเปลี่ยนแปลงส่งผลกระทบโมดูลอื่นไหม
2. **รักษา interface เดิม** — อย่าเปลี่ยน function signature ที่โมดูลอื่นเรียกใช้
3. **เพิ่ม backward compatibility** — ถ้าต้องเปลี่ยน interface ให้รองรับทั้งเก่าและใหม่ชั่วคราว

### เมื่อเพิ่มฟีเจอร์
1. **อัปเดต config files** — ถ้ามีกฎใหม่ เพิ่มใน expression_rules.json
2. **เพิ่มโฟลเดอร์ Meme** — สร้าง memes/[category]/ สำหรับท่าทางใหม่
3. **อัปเดต mapping** — แก้ meme_selector.py ให้รองรับ category ใหม่
4. **เอกสาร** — อัปเดต README/docstring ให้ครบถ้วน

---

## 🔍 Debugging Guidelines

### Performance Issues
```python
# ถ้าโปรแกรมช้า ให้เช็ค:
1. ความละเอียดกล้อง (ลดเป็น 640x480)
2. จำนวน max_num_faces (ควรเป็น 1)
3. ขนาดภาพ Meme ที่โหลด (ไม่ควรเกิน 400x400)
```

### Detection Accuracy Issues
```python
# ถ้าตรวจจับไม่แม่น:
1. เช็คแสง — ควรมีแสงส่องหน้าเพียงพอ
2. ลด min_detection_confidence
3. ปรับ threshold ใน expression_analyzer.py
```

---

## 📦 Dependencies Management

### Core Libraries
```text
opencv-python>=4.8.0      # Computer vision
mediapipe>=0.10.0         # Face/hand landmarks
fer>=2023.0.0             # Emotion recognition (optional)
Pillow>=10.0.0            # Image processing
numpy>=1.24.0             # Numerical computing
```

### Optional Libraries
```text
pygame>=2.5.0             # Advanced GUI (alternative)
tensorflow>=2.12.0        # ถ้าใช้ FER
```

---

## 🎯 Development Phases

### Phase 1: Core Infrastructure
- [ ] Camera input/output
- [ ] Basic face detection
- [ ] Display system

### Phase 2: Expression Analysis
- [ ] Landmark extraction
- [ ] Expression analyzer logic
- [ ] Config-based rules

### Phase 3: Meme Integration
- [ ] Meme loading system
- [ ] Meme selection logic
- [ ] Overlay rendering

### Phase 4: Hand Gesture (Optional)
- [ ] Hand detection
- [ ] Gesture recognition
- [ ] Priority system (gesture > expression)

### Phase 5: Polish
- [ ] Performance optimization
- [ ] Error handling
- [ ] User configuration options

---

## 🚀 Testing Strategy

### Manual Testing Checklist
```
✅ กล้องเปิดได้ปกติ
✅ ตรวจจับใบหน้าได้ในแสงปกติ
✅ แต่ละท่าทางแสดง Meme ถูกต้อง
✅ Meme เปลี่ยนเมื่อท่าทางเปลี่ยน
✅ ไม่ค้าง/กระตุก
✅ กด Q หรือ ESC ออกได้
✅ ไม่ crash เมื่อไม่มีใบหน้าในเฟรม
```

---

## ⚠️ Common Pitfalls

### 1. Camera Release
```python
# ❌ ไม่ปล่อยกล้อง
cap = cv2.VideoCapture(0)
# ... โค้ดทำงาน ...
# ลืม cap.release()

# ✅ ใช้ try-finally
try:
    cap = cv2.VideoCapture(0)
    # ... โค้ดทำงาน ...
finally:
    cap.release()
    cv2.destroyAllWindows()
```

### 2. BGR vs RGB
```python
# ❌ ส่ง BGR ไปให้ MediaPipe
results = face_mesh.process(frame)

# ✅ แปลงเป็น RGB ก่อน
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
results = face_mesh.process(rgb)
```

### 3. Landmark Index
```python
# ❌ ใช้ index ผิด
mouth_open = lm[0].y - lm[1].y  # ไม่ได้เป็นปาก!

# ✅ ใช้ index ที่ถูกต้อง (ดูจาก MediaPipe docs)
mouth_open = abs(lm[14].y - lm[13].y)
```

---

## 📚 Reference Files

เมื่อทำงานกับโปรเจคนี้ ให้อ้างอิงไฟล์ต่อไปนี้:
- `Initial.md` — โครงสร้างโปรเจคและแผนการพัฒนา
- `meme-face-detector.md` — รายละเอียดทางเทคนิคแบบเต็ม
- `config/expression_rules.json` — กฎการวิเคราะห์ท่าทาง
- `config/meme_mapping.json` — แมปท่าทาง → Meme

---

## 🔄 Version Control Strategy

### Git Workflow
```bash
main           # stable version
├── dev        # development branch
├── feature/*  # feature branches
└── fix/*      # bugfix branches
```

### Commit Message Format
```
<type>: <subject>

Types:
- feat: ฟีเจอร์ใหม่
- fix: แก้บัก
- docs: เอกสาร
- refactor: ปรับโครงสร้างโค้ด
- perf: ปรับปรุงประสิทธิภาพ
- test: เพิ่ม/แก้ไขเทส

ตัวอย่าง:
feat: add hand gesture detection
fix: camera not releasing on exit
docs: update expression rules in README
```

---

## 🎓 Learning Resources

### MediaPipe
- [Face Mesh Guide](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [Hands Guide](https://google.github.io/mediapipe/solutions/hands.html)

### OpenCV
- [Camera Capture Tutorial](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html)

### Python Best Practices
- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

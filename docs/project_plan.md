# 📅 Project Development Plan

## Current Status: Phase 4 — Meme Integration ✅

---

## Phase Checklist

### ✅ Phase 0: Project Setup (COMPLETED)

- [x] สร้างโครงสร้างโฟลเดอร์
- [x] สร้าง Context Engineering documents
- [x] สร้าง requirements.txt
- [x] สร้าง .gitignore
- [x] สร้าง README.md
- [x] สร้าง config files (JSON)
- [x] สร้าง src/__init__.py

---

### ✅ Phase 1: Core Infrastructure (COMPLETED)

- [x] `src/camera.py` — Camera input manager
- [x] `src/display.py` — Display output manager with FPS counter
- [x] `main.py` — Basic entry point (camera → display)
- [x] Test: Camera opens and displays real-time

---

### ✅ Phase 2: Face Detection (COMPLETED)

- [x] `src/detector.py` — MediaPipe Face Mesh + Hands integration
  - FaceDetector class รองรับ Face Mesh 468 landmarks
  - Hand detection 21 landmarks
  - `detect_all()` รวม 1 RGB conversion สำหรับทั้งใบหน้าและมือ
  - Debug mode: วาด landmarks บนหน้าจอ
- [x] Toggle debug landmarks ด้วยปุ่ม D ใน main.py

---

### ✅ Phase 3: Expression Analysis (COMPLETED)

- [x] `src/expression_analyzer.py` — Expression logic
  - `analyze_expression()`: surprised, happy, angry, sleepy, thinking, neutral
  - `analyze_gesture()`: thumbs_up, peace, pointing, fist
  - `get_debug_values()`: คืน metrics ทั้งหมดเพื่อ calibration
  - Integrate กับ `config/expression_rules.json`
- [x] แสดง expression/gesture บนหน้าจอ (HUD)

---

### ✅ Phase 4: Meme Integration (COMPLETED)

- [x] `src/meme_selector.py` — Meme selection engine
  - Cache ไฟล์ Meme ทุกหมวดตอนเริ่มต้น
  - Cooldown 2 วินาที ก่อนเปลี่ยน Meme
  - หลีกเลี่ยง Meme เดิมถ้ามีตัวเลือก
  - `force_next()` สำหรับปุ่ม N
- [x] `src/overlay.py` — Image overlay
  - RGBA alpha blending สำหรับ PNG โปร่งใส
  - Image cache เพื่อประสิทธิภาพ
  - รองรับ 4 ตำแหน่ง: top_left/top_right/bottom_left/bottom_right
- [x] `main.py` อัปเดต — เชื่อมทุกส่วนเข้าด้วยกัน
  - CLI arguments: --debug, --camera, --width, --height
  - Keyboard: Q/ESC=ออก, D=debug, N=next meme
  - HUD แสดง expression + gesture + debug values

---

### 🔜 Phase 5: Hand Gesture (Optional)

**Status:** Partially Done (gesture detection อยู่ใน expression_analyzer.py แล้ว)
**Remaining:**
- [ ] เพิ่ม Meme เฉพาะ gesture: fist, pointing
- [ ] อัปเดต config/meme_mapping.json สำหรับ gesture ใหม่

---

### 🔜 Phase 6: Polish & Optimization

**Status:** Not Started
**Tasks:**
- [ ] Tune detection thresholds ให้แม่นยำขึ้น
- [ ] Smoothing: ใช้ majority vote 5 frames ก่อนเปลี่ยน expression
- [ ] Command-line arguments เพิ่มเติม (--cooldown, --size, --position)
- [ ] Performance: skip processing ทุก 2 frames ถ้า FPS ต่ำ
- [ ] เพิ่มภาพ Meme จริงลงในทุกโฟลเดอร์

---

## 📊 Overall Progress

```
Phase 0: ████████████████████ 100% ✅
Phase 1: ████████████████████ 100% ✅
Phase 2: ████████████████████ 100% ✅
Phase 3: ████████████████████ 100% ✅
Phase 4: ████████████████████ 100% ✅
Phase 5: ██████░░░░░░░░░░░░░░  30% 🔄
Phase 6: ░░░░░░░░░░░░░░░░░░░░   0%

Total:   ████████████████░░░░  77%
```

---

## 🎯 Milestones

1. **MVP (Minimum Viable Product)** ✅ — End of Phase 4
   - Face detection + expression analysis + meme display

2. **Full Feature Set** 🔄 — Phase 5 gestures ส่วนใหญ่พร้อมแล้ว
   - + Hand gestures (thumbs_up, peace ทำงานแล้ว)

3. **Production Ready** — End of Phase 6

---

## 🚀 วิธีรันทันที

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# รันปกติ
python main.py

# รันพร้อม debug landmarks
python main.py --debug

# เปลี่ยน camera หรือความละเอียด
python main.py --camera 1 --width 640 --height 480
```

## 📝 ขั้นตอนถัดไป

1. **เพิ่มภาพ Meme** ลงในโฟลเดอร์ `memes/<category>/` (PNG โปร่งใสแนะนำ)
2. รันโปรแกรม แล้วกด **D** เพื่อดู landmarks + debug values
3. ปรับ thresholds ใน `config/expression_rules.json` ตาม debug values
4. เพิ่ม Meme มากขึ้นเรื่อยๆ ตามต้องการ

---

**Last Updated:** 2026-07-05  
**Current Phase:** Phase 4 ✅ → Phase 5/6 🔜

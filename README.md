# 🎭 Meme Face Detector

> ระบบตรวจจับลักษณะท่าทางและสีหน้าผ่านกล้อง แล้วแสดงภาพ Meme ตลก ๆ ตามท่าทางของคุณแบบ Real-time

---

## 📋 ภาพรวมโปรเจค

โปรเจคนี้ใช้ Python เป็นหลัก รวมเอาเทคโนโลยี Computer Vision มาวิเคราะห์ท่าทางผ่านกล้อง แล้วแสดง Meme ที่เหมาะสมกับสีหน้า/ท่าทางของผู้ใช้แบบ Real-time เมื่อท่าทางเปลี่ยน ภาพ Meme ก็จะเปลี่ยนตามทันที

---

## 🛠️ Tech Stack

- **Python 3.8+** — ภาษาหลัก
- **OpenCV** — กล้อง + แสดงผล
- **MediaPipe** — ตรวจจับใบหน้าและมือ
- **NumPy** — คำนวณทางคณิตศาสตร์
- **Pillow** — จัดการภาพ

---

## 🚀 การติดตั้ง

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/meme-face-detector.git
cd meme-face-detector
```

### 2. สร้าง Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 4. เพิ่มภาพ Meme

ใส่ภาพ Meme ของคุณลงในโฟลเดอร์ `memes/` ตามหมวดหมู่:

```
memes/
├── surprised/      # 😮 ประหลาดใจ
├── happy/          # 😂 ยิ้ม/ขำ
├── angry/          # 😠 โกรธ
├── sleepy/         # 😴 ง่วง
├── thinking/       # 🤔 คิด
├── thumbs_up/      # 👍 ยกนิ้วโป้ง
├── peace/          # ✌️ V sign
└── neutral/        # 😐 เฉยๆ
```

รองรับไฟล์: PNG, JPG, JPEG (PNG โปร่งใสแนะนำ)

---

## 💻 วิธีรัน

```bash
python main.py
```

**การควบคุม:**
- กด `Q` หรือ `ESC` เพื่อออก

---

## 📊 ท่าทางที่รองรับ

| ท่าทาง | คำอธิบาย | Meme Category |
|--------|----------|---------------|
| 😮 ประหลาดใจ | ปากเปิดกว้าง + คิ้วยกสูง | surprised |
| 😂 ยิ้ม/ขำ | มุมปากยกขึ้น | happy |
| 😠 โกรธ | คิ้วขมวด + ปากแน่น | angry |
| 😴 ง่วง/เบื่อ | ตาหลับ | sleepy |
| 🤔 คิด/สงสัย | เอียงหัว | thinking |
| 👍 ยกนิ้วโป้ง | ท่าทางมือ | thumbs_up |
| ✌️ V sign | ท่าทางมือ | peace |
| 😐 เฉยๆ | ไม่มีท่าทางชัดเจน | neutral |

---

## ⚙️ การปรับแต่ง

### ปรับความไวในการตรวจจับ

แก้ไขค่าใน `config/expression_rules.json`:

```json
{
  "surprised": {
    "mouth_open_threshold": 25,     // ลดค่า = ไวขึ้น
    "brow_raise_threshold": 15
  }
}
```

### เปลี่ยนตำแหน่ง/ขนาด Meme

แก้ไขในโค้ด `main.py`:

```python
# ปรับขนาด (กว้าง, สูง)
frame = overlay.apply(frame, meme_path, size=(300, 300))

# เปลี่ยนตำแหน่ง
frame = overlay.apply(frame, meme_path, position="bottom_right")
```

ตำแหน่งที่รองรับ: `top_left`, `top_right`, `bottom_left`, `bottom_right`

---

## 🐛 แก้ไขปัญหา

| ปัญหา | วิธีแก้ |
|-------|---------|
| กล้องไม่เปิด | ปิดโปรแกรมอื่นที่ใช้กล้อง |
| ตรวจจับไม่แม่น | เพิ่มแสงในห้อง |
| Meme ไม่แสดง | เช็คว่ามีภาพในโฟลเดอร์ memes/ |
| โปรแกรมช้า | ลดความละเอียดกล้อง |

---

## 📂 โครงสร้างโปรเจค

```
meme-face-detector/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── src/                        # Source code
│   ├── camera.py               # Camera manager
│   ├── detector.py             # Face/Hand detection
│   ├── expression_analyzer.py  # Expression logic
│   ├── meme_selector.py        # Meme selection
│   ├── overlay.py              # Image overlay
│   └── display.py              # Display manager
├── config/                     # Configuration
│   ├── expression_rules.json   # Detection rules
│   └── meme_mapping.json       # Meme mapping
└── memes/                      # Meme repository
```

---

## 🎓 เอกสารเพิ่มเติม

- [Initial.md](.kiro/steering/Initial.md) — แผนการพัฒนาและโครงสร้าง
- [generate-prp.md](.kiro/steering/generate-prp.md) — Project Requirements & Patterns
- [technical-reference.md](.kiro/steering/technical-reference.md) — ข้อมูลทางเทคนิคเชิงลึก
- [meme-face-detector.md](meme-face-detector.md) — รายละเอียดทางเทคนิคแบบเต็ม

---

## 📝 License

MIT License

---

## 👨‍💻 การพัฒนา

โปรเจคนี้ออกแบบตามหลัก **Context Engineering** เพื่อให้ง่ายต่อการทำงานร่วมกับ AI Agent

**Development Status:** 🚧 Phase 0 — Project Setup Complete

ดู [Initial.md](.kiro/steering/Initial.md) สำหรับแผนการพัฒนาแบบละเอียด

---

**สร้างด้วย ❤️ และ AI**

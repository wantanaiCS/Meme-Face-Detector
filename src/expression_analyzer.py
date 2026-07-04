"""
Expression Analyzer Module - วิเคราะห์ท่าทางใบหน้าและมือจาก landmarks
รับผิดชอบ: คำนวณ metrics จาก landmarks แล้ว map เป็น expression/gesture
"""

import json
import os
import math
from typing import Optional, Any, Tuple
import numpy as np


class ExpressionAnalyzer:
    """
    วิเคราะห์ท่าทางใบหน้าและมือจาก MediaPipe landmarks

    โหลด thresholds จาก config/expression_rules.json
    Priority: gesture (มือ) > face expression

    Args:
        config_path: path ไปยัง expression_rules.json
    """

    # ---- Face Mesh landmark indices ----
    UPPER_LIP    = 13
    LOWER_LIP    = 14
    MOUTH_LEFT   = 61
    MOUTH_RIGHT  = 291
    # คิ้วซ้าย (outer → inner)
    L_BROW_OUTER = 70
    L_BROW_INNER = 107
    # คิ้วขวา
    R_BROW_OUTER = 300
    R_BROW_INNER = 336
    # ตา
    L_EYE_TOP    = 159
    L_EYE_BOT    = 145
    R_EYE_TOP    = 386
    R_EYE_BOT    = 374
    # จมูก / forehead / chin
    NOSE_TIP     = 1
    FOREHEAD     = 10
    CHIN         = 152

    def __init__(self, config_path: str = "config/expression_rules.json"):
        self._rules = self._load_rules(config_path)
        print("📊 ExpressionAnalyzer เริ่มต้นสำเร็จ")

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    def _load_rules(self, config_path: str) -> dict:
        """โหลด expression rules จาก JSON"""
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base, config_path)

        if not os.path.isfile(full_path):
            # fallback: ใช้ relative path ตรงๆ
            full_path = config_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                rules = json.load(f)
            print(f"   โหลด expression rules จาก {full_path}")
            return rules
        except Exception as e:
            print(f"   ⚠️  โหลด config ไม่ได้ ({e}) ใช้ค่า default")
            return {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_expression(
        self,
        face_landmarks: Optional[Any],
        frame_shape: Tuple[int, int, int],
    ) -> str:
        """
        วิเคราะห์ท่าทางใบหน้าจาก landmark 468 จุด

        Args:
            face_landmarks: MediaPipe NormalizedLandmarkList หรือ None
            frame_shape: (height, width, channels) ของ frame

        Returns:
            str: ชื่อ expression เช่น "surprised", "happy", "angry",
                 "sleepy", "thinking", "neutral"
        """
        if face_landmarks is None:
            return "neutral"

        h, w = frame_shape[:2]
        lm = face_landmarks.landmark

        # ---- คำนวณ metrics ----
        mouth_open  = abs(lm[self.LOWER_LIP].y - lm[self.UPPER_LIP].y) * h
        mouth_width = abs(lm[self.MOUTH_RIGHT].x - lm[self.MOUTH_LEFT].x) * w

        # มุมปากยกขึ้น = ค่า y ของมุมปากน้อยกว่าปากบน (OpenCV y เพิ่มลงล่าง)
        mouth_corner_raise = (
            (lm[self.MOUTH_LEFT].y + lm[self.MOUTH_RIGHT].y) / 2
            - lm[self.UPPER_LIP].y
        ) * h

        # ความสูงของตา
        l_eye_open = abs(lm[self.L_EYE_BOT].y - lm[self.L_EYE_TOP].y) * h
        r_eye_open = abs(lm[self.R_EYE_BOT].y - lm[self.R_EYE_TOP].y) * h
        eye_open   = (l_eye_open + r_eye_open) / 2

        # Face height สำหรับ normalize
        face_height = abs(lm[self.CHIN].y - lm[self.FOREHEAD].y) * h
        if face_height < 1:
            face_height = h

        # Brow raise: คิ้วอยู่สูงเหนือตา → ค่ามาก = ยกสูง
        l_brow_y = (lm[self.L_BROW_OUTER].y + lm[self.L_BROW_INNER].y) / 2
        r_brow_y = (lm[self.R_BROW_OUTER].y + lm[self.R_BROW_INNER].y) / 2
        brow_avg_y = (l_brow_y + r_brow_y) / 2
        brow_raise = (lm[self.L_EYE_TOP].y - brow_avg_y) * h  # บวก = คิ้วสูงกว่าตา

        # Brow furrow: ระยะห่างแนวตั้งระหว่าง inner brow กับ nose bridge
        brow_furrow = (
            abs(lm[self.L_BROW_INNER].x - lm[self.R_BROW_INNER].x) * w
        )

        # Head tilt: nose tip offset จากกึ่งกลาง (normalize ด้วย face width)
        face_width = abs(lm[self.MOUTH_RIGHT].x - lm[self.MOUTH_LEFT].x) * w
        head_tilt  = abs(lm[self.NOSE_TIP].x - 0.5) * w

        # ---- โหลด thresholds จาก config ----
        r = self._rules

        surprised_mouth  = r.get("surprised", {}).get("mouth_open_threshold", 25)
        surprised_brow   = r.get("surprised", {}).get("brow_raise_threshold", 12)

        sleepy_eye       = r.get("sleepy", {}).get("eye_open_max", 6)

        happy_corner_min = r.get("happy", {}).get("mouth_corner_raise_min", 0.015)
        happy_open_min   = r.get("happy", {}).get("mouth_open_min", 5)
        happy_open_max   = r.get("happy", {}).get("mouth_open_max", 25)

        angry_furrow     = r.get("angry", {}).get("brow_furrow_threshold", 0.015)
        angry_open_max   = r.get("angry", {}).get("mouth_open_max", 8)

        thinking_tilt    = r.get("thinking", {}).get("head_tilt_min", 5)

        # ---- Priority matching (สำคัญสูง → ต่ำ) ----

        # 1. Surprised: ปากเปิดกว้าง + คิ้วยกสูง
        if mouth_open > surprised_mouth and brow_raise > surprised_brow:
            return "surprised"

        # 2. Sleepy: ตาหลับเกือบสนิท
        if eye_open < sleepy_eye:
            return "sleepy"

        # 3. Happy: มุมปากยกขึ้น + ปากเปิดกลาง
        # mouth_corner_raise < 0 หมายความว่ามุมปากอยู่เหนือ upper_lip (ยิ้ม)
        if (mouth_corner_raise < -(happy_corner_min * h)
                and happy_open_min < mouth_open < happy_open_max):
            return "happy"

        # 4. Angry: คิ้วขมวด (inner brow ชิดกัน) + ปากแน่น
        face_w_norm = face_width if face_width > 1 else w * 0.3
        if (brow_furrow < face_w_norm * (1 - angry_furrow)
                and mouth_open < angry_open_max):
            return "angry"

        # 5. Thinking: เอียงหัว
        if head_tilt > thinking_tilt:
            return "thinking"

        return "neutral"

    def analyze_gesture(
        self,
        hand_landmarks: Optional[Any],
        frame_shape: Tuple[int, int, int],
    ) -> Optional[str]:
        """
        วิเคราะห์ท่าทางมือจาก landmark 21 จุด

        Args:
            hand_landmarks: MediaPipe NormalizedLandmarkList หรือ None
            frame_shape: (height, width, channels)

        Returns:
            str: "thumbs_up", "peace", "pointing", "fist" หรือ None
        """
        if hand_landmarks is None:
            return None

        lm = hand_landmarks.landmark

        # ---- ตรวจสอบนิ้วแต่ละนิ้วว่ายื่นหรือไม่ ----
        # นิ้วโป้ง: เทียบ x (เพราะพับซ้าย-ขวา ไม่ใช่บน-ล่าง)
        # ใช้ y เปรียบเทียบ tip กับ 2nd knuckle (pip) สำหรับนิ้วอื่น
        thumb_up  = lm[4].y < lm[3].y < lm[2].y   # tip < ip < mcp (y น้อย = สูงกว่า)
        index_up  = lm[8].y  < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up   = lm[16].y < lm[14].y
        pinky_up  = lm[20].y < lm[18].y

        fingers_up = [index_up, middle_up, ring_up, pinky_up]
        num_up     = sum(fingers_up)

        # ---- Gesture matching ----

        # 👍 Thumbs Up: เฉพาะนิ้วโป้งยกขึ้น, นิ้วอื่นพับ
        if thumb_up and num_up == 0:
            return "thumbs_up"

        # ✌️ Peace / V sign: นิ้วชี้ + กลางยื่น, นิ้วนางและก้อยพับ
        if index_up and middle_up and not ring_up and not pinky_up:
            return "peace"

        # ☝️ Pointing: เฉพาะนิ้วชี้ยื่น
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "pointing"

        # ✊ Fist: ทุกนิ้วพับ
        if not thumb_up and num_up == 0:
            return "fist"

        return None

    # ------------------------------------------------------------------
    # Debug helper
    # ------------------------------------------------------------------

    def get_debug_values(
        self,
        face_landmarks: Optional[Any],
        frame_shape: Tuple[int, int, int],
    ) -> dict:
        """
        คืนค่า metrics ทั้งหมดเพื่อ calibration / debug

        Returns:
            dict ของค่า metrics ต่างๆ
        """
        if face_landmarks is None:
            return {}

        h, w = frame_shape[:2]
        lm = face_landmarks.landmark

        mouth_open = abs(lm[self.LOWER_LIP].y - lm[self.UPPER_LIP].y) * h
        l_eye_open = abs(lm[self.L_EYE_BOT].y - lm[self.L_EYE_TOP].y) * h
        r_eye_open = abs(lm[self.R_EYE_BOT].y - lm[self.R_EYE_TOP].y) * h
        eye_open   = (l_eye_open + r_eye_open) / 2

        l_brow_y   = (lm[self.L_BROW_OUTER].y + lm[self.L_BROW_INNER].y) / 2
        r_brow_y   = (lm[self.R_BROW_OUTER].y + lm[self.R_BROW_INNER].y) / 2
        brow_avg_y = (l_brow_y + r_brow_y) / 2
        brow_raise = (lm[self.L_EYE_TOP].y - brow_avg_y) * h

        mouth_corner_raise = (
            (lm[self.MOUTH_LEFT].y + lm[self.MOUTH_RIGHT].y) / 2
            - lm[self.UPPER_LIP].y
        ) * h

        head_tilt = abs(lm[self.NOSE_TIP].x - 0.5) * w
        brow_furrow = abs(lm[self.L_BROW_INNER].x - lm[self.R_BROW_INNER].x) * w

        return {
            "mouth_open":        round(mouth_open, 2),
            "eye_open":          round(eye_open, 2),
            "brow_raise":        round(brow_raise, 2),
            "mouth_corner_raise":round(mouth_corner_raise, 2),
            "head_tilt":         round(head_tilt, 2),
            "brow_furrow":       round(brow_furrow, 2),
        }


# ทดสอบโมดูลเดี่ยว
if __name__ == "__main__":
    import sys, cv2
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.camera import Camera
    from src.detector import FaceDetector

    print("🧪 ทดสอบ ExpressionAnalyzer")

    camera   = Camera(camera_id=0, width=640, height=480)
    detector = FaceDetector(draw_landmarks=True)
    analyzer = ExpressionAnalyzer()

    print("กด 'Q' เพื่อออก")
    while True:
        frame = camera.read_frame()
        if frame is None:
            break

        face_lm, hand_lm = detector.detect_all(frame)
        expression = analyzer.analyze_expression(face_lm, frame.shape)
        gesture    = analyzer.analyze_gesture(hand_lm, frame.shape)

        label = gesture if gesture else expression

        cv2.putText(frame, f"State: {label}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2, cv2.LINE_AA)

        # แสดง debug values
        dbg = analyzer.get_debug_values(face_lm, frame.shape)
        y = 80
        for k, v in dbg.items():
            cv2.putText(frame, f"{k}: {v}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
            y += 20

        cv2.imshow("Expression Test", frame)
        if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q"), 27):
            break

    camera.release()
    detector.release()
    cv2.destroyAllWindows()
    print("✅ ทดสอบเสร็จสิ้น")

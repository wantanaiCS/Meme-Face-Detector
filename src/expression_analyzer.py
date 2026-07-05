"""
Expression Analyzer Module - วิเคราะห์ท่าทางใบหน้าและมือ

Strategy (ลำดับการตัดสิน):
  1. Blendshapes  — ถ้า face_result.blendshapes มีข้อมูล ใช้เป็นหลัก (แม่นกว่า)
  2. Geometry     — fallback เมื่อไม่มี blendshapes (ใช้ landmark ratio)

Face expressions ที่รองรับ:
  laughing  — ยิ้มกว้างมาก + ปากเปิด
  wink      — ตากะพริบข้างเดียว (L/R ต่างกันมาก)
  derp      — ยื่นลิ้น (tongueOut)
  rage      — โกรธจัด: คิ้วขมวดแน่น + ปากเปิด
  sigma     — หน้า sigma: คิ้วกลางยก + ปากจู๋แน่น (ไม่ยิ้ม ไม่เศร้า)
  confused  — งง: คิ้วยกข้างเดียว + ปากเบี้ยว
  sad       — เศร้า: คิ้วกลางยก + มุมปากตก
  surprised — ปากเปิดกว้าง + คิ้วกลางยกสูง
  happy     — ยิ้มชัด
  angry     — คิ้วขมวด + ปากแน่น
  sleepy    — ตาหลับทั้งสองข้าง
  thinking  — ปากจู๋/เม้ม
  neutral   — default

Hand gestures ที่รองรับ:
  middle_finger — โชว์นิ้วกลาง
  ok_sign       — โอเค (นิ้วโป้ง + นิ้วชี้จรดกัน)
  thumbs_up     — 👍
  peace         — ✌️
  pointing      — ☝️
  fist          — ✊
"""

import json
import math
import os
from typing import Optional, Any, Tuple


class ExpressionAnalyzer:
    """
    วิเคราะห์ท่าทางใบหน้าและมือ

    Args:
        config_path: path ไปยัง expression_rules.json
    """

    # ---- Face Mesh landmark indices (geometry fallback) ----
    UPPER_LIP    = 13
    LOWER_LIP    = 14
    MOUTH_LEFT   = 61
    MOUTH_RIGHT  = 291
    L_BROW_OUTER = 70
    L_BROW_INNER = 107
    R_BROW_OUTER = 300
    R_BROW_INNER = 336
    L_EYE_TOP    = 159
    L_EYE_BOT    = 145
    R_EYE_TOP    = 386
    R_EYE_BOT    = 374
    NOSE_TIP     = 1
    FOREHEAD     = 10
    CHIN         = 152

    def __init__(self, config_path: str = "config/expression_rules.json"):
        self._rules = self._load_rules(config_path)
        # hysteresis: ต้องเห็น expression ใหม่ติดกัน N frames ก่อนเปลี่ยน
        self._last_expression: str = "neutral"
        self._candidate: str       = "neutral"
        self._candidate_count: int = 0
        self._CONFIRM_FRAMES: int  = 3   # ปรับได้ใน rules
        print("📊 ExpressionAnalyzer เริ่มต้นสำเร็จ (Blendshapes + Geometry)")

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_rules(self, config_path: str) -> dict:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base, config_path)
        if not os.path.isfile(full_path):
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
        face_result: Optional[Any],
        frame_shape: Tuple[int, int, int],
    ) -> str:
        """
        วิเคราะห์สีหน้าพร้อม hysteresis

        ต้องเห็น expression ใหม่ติดกัน CONFIRM_FRAMES ก่อนเปลี่ยน
        ป้องกัน neutral ← → expression flickering

        Returns:
            "laughing" | "wink" | "derp" | "rage" | "sigma" | "confused" | "sad" |
            "surprised" | "happy" | "angry" | "sleepy" | "thinking" | "neutral"
        """
        if face_result is None:
            return self._last_expression

        bs = getattr(face_result, "blendshapes", {})
        if bs:
            nose_x = 0.5
            lm = getattr(face_result, "landmark", None)
            if lm and len(lm) > self.NOSE_TIP:
                nose_x = lm[self.NOSE_TIP].x
            raw = self._analyze_blendshapes(bs, nose_x)
        else:
            raw = self._analyze_geometry(face_result, frame_shape)

        confirm = self._rules.get("hysteresis", {}).get("confirm_frames",
                                                         self._CONFIRM_FRAMES)

        if raw == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate       = raw
            self._candidate_count = 1

        # ต้องเห็น expression เดิมติดกันครบ confirm frames ถึงจะเปลี่ยน
        # ทั้ง expression ใหม่ และ neutral ต้องรอเท่ากัน — ลด flickering ทุกทิศทาง
        if self._candidate_count >= confirm:
            self._last_expression = raw

        return self._last_expression

    def analyze_gesture(
        self,
        hand_result: Optional[Any],
        frame_shape: Tuple[int, int, int],
    ) -> Optional[str]:
        """
        วิเคราะห์ท่าทางมือ

        Returns:
            "middle_finger" | "ok_sign" | "thumbs_up" | "peace" |
            "pointing" | "fist" | None
        """
        if hand_result is None:
            return None

        lm = hand_result.landmark

        # ตรวจทิศทางมือ: wrist(0) อยู่ใต้ middle_mcp(9) = มือชี้ขึ้น
        hand_up = lm[0].y > lm[9].y

        if hand_up:
            thumb_up  = lm[4].y  < lm[2].y
            index_up  = lm[8].y  < lm[5].y
            middle_up = lm[12].y < lm[9].y
            ring_up   = lm[16].y < lm[13].y
            pinky_up  = lm[20].y < lm[17].y
        else:
            thumb_up  = lm[4].y  > lm[2].y
            index_up  = lm[8].y  > lm[5].y
            middle_up = lm[12].y > lm[9].y
            ring_up   = lm[16].y > lm[13].y
            pinky_up  = lm[20].y > lm[17].y

        num_fingers = sum([index_up, middle_up, ring_up, pinky_up])

        # 🖕 Middle Finger — นิ้วกลางชี้ขึ้น ส่วนที่เหลือหุบ
        if middle_up and not index_up and not ring_up and not pinky_up:
            return "middle_finger"

        # 👌 OK Sign — นิ้วโป้งกับนิ้วชี้ปลายจรดกัน (distance น้อย)
        thumb_tip = lm[4]
        index_tip = lm[8]
        ok_dist = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
        ok_threshold = self._rules.get("ok_sign", {}).get("tip_distance_max", 0.07)
        if ok_dist < ok_threshold and middle_up and ring_up and pinky_up:
            return "ok_sign"

        # 👍 Thumbs Up
        if thumb_up and not index_up and not middle_up and not ring_up:
            return "thumbs_up"

        # ✌️ Peace / V sign
        if index_up and middle_up and not ring_up and not pinky_up:
            return "peace"

        # ☝️ Pointing
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "pointing"

        # ✊ Fist
        if not thumb_up and num_fingers == 0:
            return "fist"

        return None

    def get_debug_values(
        self,
        face_result: Optional[Any],
        frame_shape: Tuple[int, int, int],
    ) -> dict:
        """คืนค่าที่ใช้ตัดสิน expression ทั้งหมด เพื่อแสดงใน debug HUD"""
        if face_result is None:
            return {}

        bs = getattr(face_result, "blendshapes", {})

        if bs:
            keys = [
                "mouthSmileLeft", "mouthSmileRight",
                "jawOpen",
                "browInnerUp",
                "browDownLeft", "browDownRight",
                "eyeBlinkLeft", "eyeBlinkRight",
                "mouthFunnel", "mouthPucker",
                "tongueOut",
                "mouthFrownLeft", "mouthFrownRight",
                "browOuterUpLeft", "browOuterUpRight",
                "mouthLeft", "mouthRight",
            ]
            result = {k: round(bs.get(k, 0.0), 3) for k in keys}
            # เพิ่ม head_tilt คำนวณจาก nose landmark
            lm = getattr(face_result, "landmark", None)
            if lm and len(lm) > self.NOSE_TIP:
                result["headTilt"] = round(abs(lm[self.NOSE_TIP].x - 0.5), 3)
            return result
        else:
            return self._geometry_debug(face_result, frame_shape)

    # ------------------------------------------------------------------
    # Blendshapes path (แม่น, ใช้เป็นหลัก)
    # ------------------------------------------------------------------

    def _analyze_blendshapes(self, bs: dict, nose_x: float = 0.5) -> str:
        """
        ตัดสิน expression จาก blendshape scores (0.0 – 1.0)
        nose_x: ตำแหน่ง x ของจมูก (0.0-1.0) ใช้คำนวณ head yaw

        Priority order (สำคัญที่สุดก่อน):
          1. derp      — tongueOut ชัดเจน
          2. wink      — ตากะพริบข้างเดียว
          3. laughing  — ยิ้มกว้างมาก + ปากเปิด
          4. rage      — โกรธจัด (คิ้วขมวด + ปากเปิด)
          5. sigma     — ปากจู๋ + คิ้วนอกยกข้างใดข้างหนึ่ง + หันหน้านิด
          6. surprised — ปากเปิดกว้าง + คิ้วกลางยก
          7. sad       — คิ้วกลางยก + มุมปากตก
          8. confused  — browOuterUp ข้างเดียว + ปากเบี้ยว
          9. sleepy    — ตาหลับทั้งสองข้าง
         10. happy     — ยิ้มชัด
         11. angry     — คิ้วขมวด + ปากแน่น
         12. thinking  — ปากจู๋/เม้ม
         13. neutral
        """
        r = self._rules

        # ---- ดึง thresholds ----
        # derp
        derp_tongue  = r.get("derp",     {}).get("tongueOut_min",      0.30)

        # wink
        wk_blink     = r.get("wink",     {}).get("blink_one_side_min", 0.60)
        wk_diff      = r.get("wink",     {}).get("blink_diff_min",     0.40)

        # laughing
        lg_smile     = r.get("laughing", {}).get("mouthSmile_min",     0.55)
        lg_jaw       = r.get("laughing", {}).get("jawOpen_min",        0.25)

        # rage
        rg_down      = r.get("rage",     {}).get("browDown_min",       0.45)
        rg_jaw       = r.get("rage",     {}).get("jawOpen_min",        0.20)

        # sigma
        sg_pucker    = r.get("sigma",    {}).get("mouthPucker_min",      0.28)
        sg_smile_max = r.get("sigma",    {}).get("mouthSmile_max",       0.15)
        sg_frown_max = r.get("sigma",    {}).get("mouthFrown_max",       0.18)
        sg_jaw_max   = r.get("sigma",    {}).get("jawOpen_max",          0.10)
        sg_down_max  = r.get("sigma",    {}).get("browDown_max",         0.25)
        sg_brow_out  = r.get("sigma",    {}).get("browOuterUp_min",      0.12)
        sg_tilt_min  = r.get("sigma",    {}).get("head_tilt_min",        0.08)

        # surprised
        s_jaw        = r.get("surprised",{}).get("jawOpen_min",        0.30)
        s_brow_inner = r.get("surprised",{}).get("browInnerUp_min",    0.15)
        s_brow_outer = r.get("surprised",{}).get("browOuterUp_min",    0.18)

        # sad
        sd_brow      = r.get("sad",      {}).get("browInnerUp_min",    0.30)
        sd_frown     = r.get("sad",      {}).get("mouthFrown_min",     0.20)

        # confused
        cf_outer     = r.get("confused", {}).get("browOuterUp_diff_min", 0.25)
        cf_mouth     = r.get("confused", {}).get("mouthAsym_min",      0.06)

        # sleepy
        sl_blink     = r.get("sleepy",   {}).get("eyeBlink_min",       0.65)

        # happy
        h_smile      = r.get("happy",    {}).get("mouthSmile_min",     0.35)

        # angry
        a_down       = r.get("angry",    {}).get("browDown_min",       0.35)
        a_jaw        = r.get("angry",    {}).get("jawOpen_max",        0.15)

        # thinking
        t_funnel     = r.get("thinking", {}).get("mouthFunnel_min",    0.20)
        t_pucker     = r.get("thinking", {}).get("mouthPucker_min",    0.20)

        # ---- ดึงค่าจาก blendshapes ----
        jaw_open      = bs.get("jawOpen",           0.0)
        brow_up       = bs.get("browInnerUp",       0.0)
        brow_down_l   = bs.get("browDownLeft",      0.0)
        brow_down_r   = bs.get("browDownRight",     0.0)
        brow_down     = (brow_down_l + brow_down_r) / 2
        brow_outer_l  = bs.get("browOuterUpLeft",   0.0)
        brow_outer_r  = bs.get("browOuterUpRight",  0.0)
        smile_l       = bs.get("mouthSmileLeft",    0.0)
        smile_r       = bs.get("mouthSmileRight",   0.0)
        smile         = (smile_l + smile_r) / 2
        blink_l       = bs.get("eyeBlinkLeft",      0.0)
        blink_r       = bs.get("eyeBlinkRight",     0.0)
        blink         = (blink_l + blink_r) / 2
        funnel        = bs.get("mouthFunnel",       0.0)
        pucker        = bs.get("mouthPucker",       0.0)
        tongue        = bs.get("tongueOut",         0.0)
        frown_l       = bs.get("mouthFrownLeft",    0.0)
        frown_r       = bs.get("mouthFrownRight",   0.0)
        frown         = (frown_l + frown_r) / 2
        mouth_left    = bs.get("mouthLeft",         0.0)
        mouth_right   = bs.get("mouthRight",        0.0)

        # ---- Priority matching ----

        # 1. Derp: ยื่นลิ้นชัด
        if tongue > derp_tongue:
            return "derp"

        # 2. Wink: ตาข้างหนึ่งหลับ ส่วนอีกข้างลืมอยู่
        blink_diff = abs(blink_l - blink_r)
        if max(blink_l, blink_r) > wk_blink and blink_diff > wk_diff:
            return "wink"

        # 3. Laughing: ยิ้มกว้างมาก + ปากเปิด
        if smile > lg_smile and jaw_open > lg_jaw:
            return "laughing"

        # 4. Rage: คิ้วขมวดแน่น + ปากเปิด (โกรธแล้วตะโกน)
        if brow_down > rg_down and jaw_open > rg_jaw:
            return "rage"

        # 5. Sigma: ปากจู๋แน่น + คิ้วนอกยกข้างใดข้างหนึ่ง + หันหน้านิด
        #    mouthPucker ↑  browOuterUp (L หรือ R) ↑  nose ไม่อยู่กึ่งกลาง
        brow_outer_max = max(brow_outer_l, brow_outer_r)
        head_tilt      = abs(nose_x - 0.5)   # 0 = หน้าตรง, >0.08 = หันนิด
        if (pucker > sg_pucker
                and brow_outer_max > sg_brow_out
                and head_tilt > sg_tilt_min
                and smile < sg_smile_max
                and frown < sg_frown_max
                and jaw_open < sg_jaw_max
                and brow_down < sg_down_max):
            return "sigma"

        # 6. Surprised: ปากเปิดกว้าง + คิ้วยกขึ้น (inner OR outer — รองรับทุกโครงสร้างใบหน้า)
        brow_outer_avg = (brow_outer_l + brow_outer_r) / 2
        brow_any_up = brow_up > s_brow_inner or brow_outer_avg > s_brow_outer
        if jaw_open > s_jaw and brow_any_up:
            return "surprised"

        # 7. Sad: คิ้วกลางยก + มุมปากตก
        if brow_up > sd_brow and frown > sd_frown:
            return "sad"

        # 8. Confused: คิ้วนอกยกข้างเดียว + ปากเบี้ยว
        brow_outer_diff = abs(brow_outer_l - brow_outer_r)
        mouth_asym = abs(mouth_left - mouth_right)
        if brow_outer_diff > cf_outer and mouth_asym > cf_mouth:
            return "confused"

        # 9. Sleepy: ตาหลับทั้งสองข้าง
        if blink > sl_blink:
            return "sleepy"

        # 10. Happy: ยิ้มชัด
        if smile > h_smile:
            return "happy"

        # 11. Angry: คิ้วขมวด + ปากแน่น
        if brow_down > a_down and jaw_open < a_jaw:
            return "angry"

        # 12. Thinking: ปากจู๋หรือเม้ม
        if funnel > t_funnel or pucker > t_pucker:
            return "thinking"

        return "neutral"

    # ------------------------------------------------------------------
    # Geometry path (fallback เมื่อไม่มี blendshapes)
    # ------------------------------------------------------------------

    def _analyze_geometry(
        self,
        face_result: Any,
        frame_shape: Tuple[int, int, int],
    ) -> str:
        m = self._geometry_metrics(face_result.landmark)
        r = self._rules

        s_mouth = r.get("surprised", {}).get("mouth_open_ratio",      0.20)
        s_brow  = r.get("surprised", {}).get("brow_raise_ratio",      0.12)
        sl_eye  = r.get("sleepy",    {}).get("eye_open_max_ratio",    0.025)
        h_smile = r.get("happy",     {}).get("smile_ratio_min",       0.025)
        h_min   = r.get("happy",     {}).get("mouth_open_min_ratio",  0.02)
        h_max   = r.get("happy",     {}).get("mouth_open_max_ratio",  0.25)
        a_furr  = r.get("angry",     {}).get("brow_furrow_max",       0.72)
        a_open  = r.get("angry",     {}).get("mouth_open_max_ratio",  0.07)
        t_tilt  = r.get("thinking",  {}).get("head_tilt_min",         0.30)

        # Geometry fallback รองรับเฉพาะ expressions หลัก
        if m["mouth_open"] > s_mouth and m["brow_raise"] > s_brow:
            return "surprised"
        if m["eye_open"] < sl_eye:
            return "sleepy"
        if m["smile_ratio"] > h_smile and h_min < m["mouth_open"] < h_max:
            return "happy"
        if m["brow_furrow"] < a_furr and m["mouth_open"] < a_open:
            return "angry"
        if m["head_tilt"] > t_tilt:
            return "thinking"
        return "neutral"

    def _geometry_metrics(self, lm: list) -> dict:
        """คำนวณ geometry metrics (ratio เทียบกับ face_height)"""
        face_h = abs(lm[self.CHIN].y - lm[self.FOREHEAD].y)
        if face_h < 0.01:
            face_h = 0.30

        mouth_open  = abs(lm[self.LOWER_LIP].y - lm[self.UPPER_LIP].y) / face_h
        mouth_w     = abs(lm[self.MOUTH_RIGHT].x - lm[self.MOUTH_LEFT].x)
        corner_y    = (lm[self.MOUTH_LEFT].y + lm[self.MOUTH_RIGHT].y) / 2
        smile_ratio = (lm[self.UPPER_LIP].y - corner_y) / face_h

        l_eye    = abs(lm[self.L_EYE_BOT].y - lm[self.L_EYE_TOP].y) / face_h
        r_eye    = abs(lm[self.R_EYE_BOT].y - lm[self.R_EYE_TOP].y) / face_h
        eye_open = (l_eye + r_eye) / 2

        l_brow     = (lm[self.L_BROW_OUTER].y + lm[self.L_BROW_INNER].y) / 2
        r_brow     = (lm[self.R_BROW_OUTER].y + lm[self.R_BROW_INNER].y) / 2
        eye_top    = (lm[self.L_EYE_TOP].y + lm[self.R_EYE_TOP].y) / 2
        brow_raise = (eye_top - (l_brow + r_brow) / 2) / face_h

        gap         = abs(lm[self.L_BROW_INNER].x - lm[self.R_BROW_INNER].x)
        brow_furrow = gap / mouth_w if mouth_w > 0.01 else 1.0

        head_tilt = abs(lm[self.NOSE_TIP].x - 0.5) / 0.5

        return {
            "mouth_open":  mouth_open,
            "smile_ratio": smile_ratio,
            "eye_open":    eye_open,
            "brow_raise":  brow_raise,
            "brow_furrow": brow_furrow,
            "head_tilt":   head_tilt,
        }

    def _geometry_debug(
        self,
        face_result: Any,
        frame_shape: Tuple[int, int, int],
    ) -> dict:
        m = self._geometry_metrics(face_result.landmark)
        return {k: round(v, 4) for k, v in m.items()}

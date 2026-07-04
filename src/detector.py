"""
Detector Module - ตรวจจับใบหน้าและมือด้วย MediaPipe Tasks API (0.10.x)
รับผิดชอบ: Face Landmarker (478 landmarks), Hand Landmarker (21 จุด)
"""

import cv2
import mediapipe as mp
import numpy as np
import os
from typing import Optional, Tuple, Any

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark


class FaceLandmarksResult:
    """Wrapper ให้ใช้ลักษณะเดียวกับ solutions API เดิม (lm[index].x/y/z)"""

    def __init__(self, landmarks: list):
        self.landmark = landmarks  # list[NormalizedLandmark]


class FaceDetector:
    """
    ตรวจจับใบหน้าและมือด้วย MediaPipe Tasks API

    Args:
        model_dir: โฟลเดอร์ที่เก็บไฟล์ .task model
        max_num_faces: จำนวนใบหน้าสูงสุด
        max_num_hands: จำนวนมือสูงสุด
        face_detection_confidence: ความมั่นใจขั้นต่ำในการตรวจจับใบหน้า
        hand_detection_confidence: ความมั่นใจขั้นต่ำในการตรวจจับมือ
        draw_landmarks: วาด landmarks บนภาพเพื่อ debug
    """

    def __init__(
        self,
        model_dir: str = "models",
        max_num_faces: int = 1,
        max_num_hands: int = 2,
        face_detection_confidence: float = 0.5,
        hand_detection_confidence: float = 0.7,
        draw_landmarks: bool = False,
    ):
        self.draw_landmarks = draw_landmarks

        # หา model files
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        face_model = os.path.join(base, model_dir, "face_landmarker.task")
        hand_model = os.path.join(base, model_dir, "hand_landmarker.task")

        if not os.path.isfile(face_model):
            raise FileNotFoundError(
                f"ไม่พบไฟล์ {face_model}\n"
                "กรุณาดาวน์โหลด: https://storage.googleapis.com/mediapipe-models/"
                "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            )
        if not os.path.isfile(hand_model):
            raise FileNotFoundError(
                f"ไม่พบไฟล์ {hand_model}\n"
                "กรุณาดาวน์โหลด: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            )

        # ---- Face Landmarker ----
        face_opts = mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=face_model),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=max_num_faces,
            min_face_detection_confidence=face_detection_confidence,
            min_face_presence_confidence=face_detection_confidence,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
        )
        self._face_landmarker = mp_vision.FaceLandmarker.create_from_options(face_opts)

        # ---- Hand Landmarker ----
        hand_opts = mp_vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=hand_model),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_hands=max_num_hands,
            min_hand_detection_confidence=hand_detection_confidence,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._hand_landmarker = mp_vision.HandLandmarker.create_from_options(hand_opts)

        print("🧠 FaceDetector เริ่มต้นสำเร็จ (MediaPipe Tasks API)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_faces(self, frame: np.ndarray) -> Optional[FaceLandmarksResult]:
        """ตรวจจับ Face landmarks จาก BGR frame"""
        mp_image = self._to_mp_image(frame)
        result = self._face_landmarker.detect(mp_image)
        if result.face_landmarks:
            lm = self._wrap_landmarks(result.face_landmarks[0])
            if self.draw_landmarks:
                self._draw_face_landmarks(frame, result.face_landmarks[0])
            return lm
        return None

    def detect_hands(self, frame: np.ndarray) -> Optional[FaceLandmarksResult]:
        """ตรวจจับ Hand landmarks จาก BGR frame"""
        mp_image = self._to_mp_image(frame)
        result = self._hand_landmarker.detect(mp_image)
        if result.hand_landmarks:
            lm = self._wrap_landmarks(result.hand_landmarks[0])
            if self.draw_landmarks:
                self._draw_hand_landmarks(frame, result.hand_landmarks[0])
            return lm
        return None

    def detect_all(
        self, frame: np.ndarray
    ) -> Tuple[Optional[FaceLandmarksResult], Optional[FaceLandmarksResult]]:
        """ตรวจจับทั้งใบหน้าและมือใน 1 รอบ"""
        mp_image = self._to_mp_image(frame)

        face_result = self._face_landmarker.detect(mp_image)
        hand_result = self._hand_landmarker.detect(mp_image)

        face_lm = None
        hand_lm = None

        if face_result.face_landmarks:
            face_lm = self._wrap_landmarks(face_result.face_landmarks[0])
            if self.draw_landmarks:
                self._draw_face_landmarks(frame, face_result.face_landmarks[0])

        if hand_result.hand_landmarks:
            hand_lm = self._wrap_landmarks(hand_result.hand_landmarks[0])
            if self.draw_landmarks:
                self._draw_hand_landmarks(frame, hand_result.hand_landmarks[0])

        return face_lm, hand_lm

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_mp_image(frame: np.ndarray) -> mp.Image:
        """แปลง BGR frame เป็น MediaPipe Image (RGB)"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    @staticmethod
    def _wrap_landmarks(landmarks: list) -> FaceLandmarksResult:
        """Wrap list of NormalizedLandmark เป็น FaceLandmarksResult"""
        return FaceLandmarksResult(landmarks)

    def _draw_face_landmarks(self, frame: np.ndarray, landmarks: list) -> None:
        """วาด face mesh contour เพื่อ debug"""
        h, w = frame.shape[:2]
        # วาดจุดสำคัญเท่านั้น (ไม่วาดทุก 478 จุดเพื่อความเร็ว)
        key_indices = [13, 14, 61, 291, 70, 107, 300, 336,
                       159, 145, 386, 374, 1, 10, 152]
        for idx in key_indices:
            if idx < len(landmarks):
                lm = landmarks[idx]
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    def _draw_hand_landmarks(self, frame: np.ndarray, landmarks: list) -> None:
        """วาด hand landmarks เพื่อ debug"""
        h, w = frame.shape[:2]
        # Hand connections: คู่ index ที่เชื่อมกัน
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),           # นิ้วโป้ง
            (0, 5), (5, 6), (6, 7), (7, 8),            # นิ้วชี้
            (9, 10), (10, 11), (11, 12),                # นิ้วกลาง
            (13, 14), (14, 15), (15, 16),               # นิ้วนาง
            (0, 17), (17, 18), (18, 19), (19, 20),      # นิ้วก้อย
            (5, 9), (9, 13), (13, 17),                  # palm
        ]
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for i, pt in enumerate(pts):
            cv2.circle(frame, pt, 4, (255, 128, 0), -1)
        for a, b in connections:
            if a < len(pts) and b < len(pts):
                cv2.line(frame, pts[a], pts[b], (255, 200, 0), 1)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def release(self) -> None:
        """ปิด models"""
        try:
            self._face_landmarker.close()
        except Exception:
            pass
        try:
            self._hand_landmarker.close()
        except Exception:
            pass
        print("🧠 FaceDetector ปิดแล้ว")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def __del__(self):
        try:
            self.release()
        except Exception:
            pass

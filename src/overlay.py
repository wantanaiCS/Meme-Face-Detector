"""
Overlay Module - วางซ้อน Meme ลงบนภาพกล้อง
รับผิดชอบ: โหลดภาพ Meme, ปรับขนาด, alpha blending (RGBA + RGB)
"""

import cv2
import numpy as np
import os
from typing import Optional, Tuple


class MemeOverlay:
    """
    วางซ้อนภาพ Meme ลงบน frame ของกล้อง

    รองรับ:
    - PNG โปร่งใส (RGBA) → alpha blending
    - JPG / RGB → วางทับตรงๆ
    - ตำแหน่ง: top_left, top_right, bottom_left, bottom_right

    Args:
        cache_images: pre-load และ cache ภาพเพื่อความเร็ว (default: True)
        padding: ระยะห่างจากขอบ frame ในหน่วย pixel (default: 10)
    """

    POSITIONS = ("top_left", "top_right", "bottom_left", "bottom_right")

    def __init__(self, cache_images: bool = True, padding: int = 10):
        self.cache_images = cache_images
        self.padding      = padding
        self._cache: dict[str, Optional[np.ndarray]] = {}
        print("🔲 MemeOverlay เริ่มต้นสำเร็จ")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def apply(
        self,
        frame:    np.ndarray,
        meme_path: Optional[str],
        position: str = "top_right",
        size:     Tuple[int, int] = (280, 280),
    ) -> np.ndarray:
        """
        วาง Meme ลงบน frame

        Args:
            frame:     BGR frame จากกล้อง (จะถูก modify in-place)
            meme_path: path ไฟล์ Meme หรือ None
            position:  "top_left" | "top_right" | "bottom_left" | "bottom_right"
            size:      (width, height) ของ Meme ที่จะแสดง

        Returns:
            frame ที่มี Meme ซ้อนทับแล้ว (อ้างอิงเดิม)
        """
        if meme_path is None:
            return frame

        meme = self._load_meme(meme_path, size)
        if meme is None:
            return frame

        fh, fw = frame.shape[:2]
        mh, mw = meme.shape[:2]

        x, y = self._calc_position(position, fw, fh, mw, mh)

        # ตัดขอบกรณี Meme ใหญ่เกิน frame
        x = max(0, min(x, fw - 1))
        y = max(0, min(y, fh - 1))
        mw_clipped = min(mw, fw - x)
        mh_clipped = min(mh, fh - y)

        meme_crop = meme[:mh_clipped, :mw_clipped]

        roi = frame[y:y + mh_clipped, x:x + mw_clipped]

        if meme.shape[2] == 4:
            # RGBA → alpha blending
            self._blend_rgba(roi, meme_crop)
        else:
            # RGB → วางทับตรงๆ
            frame[y:y + mh_clipped, x:x + mw_clipped] = meme_crop

        return frame

    def clear_cache(self) -> None:
        """ล้าง image cache"""
        self._cache.clear()
        print("🔄 ล้าง Meme cache แล้ว")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_meme(
        self, path: str, size: Tuple[int, int]
    ) -> Optional[np.ndarray]:
        """
        โหลดและ resize ภาพ Meme

        Cache key รวม size เพื่อให้ resize แค่ครั้งเดียวต่อ size
        """
        cache_key = f"{path}::{size[0]}x{size[1]}"

        if self.cache_images and cache_key in self._cache:
            return self._cache[cache_key]

        if not os.path.isfile(path):
            if self.cache_images:
                self._cache[cache_key] = None
            return None

        # โหลดด้วย IMREAD_UNCHANGED เพื่อรักษา alpha channel
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        if img is None:
            if self.cache_images:
                self._cache[cache_key] = None
            return None

        # ถ้าเป็น grayscale → แปลงเป็น BGR
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # Resize ด้วย INTER_AREA (คุณภาพดีเมื่อลดขนาด)
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)

        if self.cache_images:
            self._cache[cache_key] = img

        return img

    def _calc_position(
        self,
        position: str,
        fw: int, fh: int,
        mw: int, mh: int,
    ) -> Tuple[int, int]:
        """คำนวณพิกัด (x, y) บน frame"""
        p = self.padding
        if position == "top_left":
            return p, p
        elif position == "top_right":
            return fw - mw - p, p
        elif position == "bottom_left":
            return p, fh - mh - p
        elif position == "bottom_right":
            return fw - mw - p, fh - mh - p
        else:
            return fw - mw - p, p  # default: top_right

    @staticmethod
    def _blend_rgba(roi: np.ndarray, meme: np.ndarray) -> None:
        """
        Alpha blending แบบ in-place บน roi

        meme ต้องมี 4 channels (BGRA)
        roi และ meme ต้องมีขนาดเท่ากัน
        """
        alpha = meme[:, :, 3:4].astype(np.float32) / 255.0  # (H, W, 1)
        meme_bgr = meme[:, :, :3].astype(np.float32)
        roi_f    = roi.astype(np.float32)

        blended = alpha * meme_bgr + (1.0 - alpha) * roi_f
        roi[:] = blended.astype(np.uint8)


# ทดสอบโมดูลเดี่ยว
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.camera import Camera

    print("🧪 ทดสอบ MemeOverlay")
    print("วางภาพทดสอบลงใน memes/neutral/ ก่อนรัน")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_dir = os.path.join(base_dir, "memes", "neutral")
    test_files = [
        os.path.join(test_dir, f)
        for f in os.listdir(test_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ] if os.path.isdir(test_dir) else []

    camera  = Camera(camera_id=0, width=640, height=480)
    overlay = MemeOverlay()

    print("กด 'Q' เพื่อออก")
    while True:
        frame = camera.read_frame()
        if frame is None:
            break

        if test_files:
            overlay.apply(frame, test_files[0], position="top_right", size=(200, 200))

        cv2.imshow("Overlay Test", frame)
        if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q"), 27):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("✅ ทดสอบเสร็จสิ้น")

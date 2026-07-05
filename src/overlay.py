"""
Overlay Module - วางซ้อน Meme ลงบนภาพกล้อง
รับผิดชอบ: โหลดภาพ Meme, ปรับขนาด, alpha blending (RGBA + RGB)
รองรับ: PNG, JPG, GIF (animated)
"""

import cv2
import numpy as np
import os
import time
from typing import Optional, Tuple, List
from PIL import Image


class MemeOverlay:
    """
    วางซ้อนภาพ Meme ลงบน frame ของกล้อง

    รองรับ:
    - PNG โปร่งใส (RGBA) → alpha blending
    - JPG / RGB → วางทับตรงๆ
    - GIF animated → เล่น animation แบบ loop โดยใช้ Pillow
    - ตำแหน่ง: top_left, top_right, bottom_left, bottom_right

    Args:
        cache_images: pre-load และ cache ภาพเพื่อความเร็ว (default: True)
        padding: ระยะห่างจากขอบ frame ในหน่วย pixel (default: 10)
    """

    POSITIONS = ("top_left", "top_right", "bottom_left", "bottom_right")

    # GIF cache entry: list of (bgra_frame, duration_sec)
    _GifFrames = List[Tuple[np.ndarray, float]]

    def __init__(self, cache_images: bool = True, padding: int = 10):
        self.cache_images = cache_images
        self.padding      = padding

        # cache สำหรับภาพนิ่ง: cache_key → np.ndarray หรือ None
        self._cache: dict[str, Optional[np.ndarray]] = {}

        # cache สำหรับ GIF: path → list of (frame_bgra, duration_sec)
        self._gif_cache: dict[str, Optional[List[Tuple[np.ndarray, float]]]] = {}

        # state สำหรับ animation: path → (start_time, size_str)
        # เก็บเวลาที่เริ่ม loop ของ GIF นั้นๆ
        self._gif_start: dict[str, float] = {}

        print("🔲 MemeOverlay เริ่มต้นสำเร็จ (รองรับ GIF animation)")

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

        # แยก GIF ออกจากภาพนิ่ง
        if meme_path.lower().endswith(".gif"):
            meme = self._get_gif_frame(meme_path, size)
        else:
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
        roi       = frame[y:y + mh_clipped, x:x + mw_clipped]

        if meme.shape[2] == 4:
            # BGRA → alpha blending
            self._blend_rgba(roi, meme_crop)
        else:
            # BGR → วางทับตรงๆ
            frame[y:y + mh_clipped, x:x + mw_clipped] = meme_crop

        return frame

    def clear_cache(self) -> None:
        """ล้าง image cache ทั้งหมด"""
        self._cache.clear()
        self._gif_cache.clear()
        self._gif_start.clear()
        print("🔄 ล้าง Meme cache แล้ว")

    # ------------------------------------------------------------------
    # GIF support
    # ------------------------------------------------------------------

    def _get_gif_frame(
        self, path: str, size: Tuple[int, int]
    ) -> Optional[np.ndarray]:
        """
        คืน frame ปัจจุบันของ GIF ตาม real-time clock

        GIF แต่ละไฟล์จะ loop อัตโนมัติโดยอ้างอิงเวลาจาก time.monotonic()
        """
        cache_key = f"{path}::{size[0]}x{size[1]}"

        # โหลด frames ถ้ายังไม่มีใน cache
        if cache_key not in self._gif_cache:
            self._gif_cache[cache_key] = self._load_gif(path, size)
            self._gif_start[cache_key] = time.monotonic()

        frames = self._gif_cache[cache_key]
        if not frames:
            return None

        # GIF มีแค่ 1 frame → คืนเลย ไม่ต้องคำนวณ
        if len(frames) == 1:
            return frames[0][0]

        # คำนวณ total duration ของ 1 รอบ
        total_dur = sum(d for _, d in frames)
        if total_dur <= 0:
            return frames[0][0]

        # หา elapsed ภายใน loop ปัจจุบัน
        elapsed = (time.monotonic() - self._gif_start[cache_key]) % total_dur

        # หา frame ที่ตรงกับเวลา
        acc = 0.0
        for frame_img, dur in frames:
            acc += dur
            if elapsed < acc:
                return frame_img

        return frames[-1][0]

    def _load_gif(
        self, path: str, size: Tuple[int, int]
    ) -> Optional[List[Tuple[np.ndarray, float]]]:
        """
        โหลด GIF ทุก frame ด้วย Pillow แล้วแปลงเป็น BGRA numpy array

        Returns:
            list of (bgra_ndarray, duration_sec) หรือ None ถ้าโหลดไม่ได้
        """
        if not os.path.isfile(path):
            print(f"   ⚠️  ไม่พบไฟล์ GIF: {path}")
            return None

        try:
            pil_gif = Image.open(path)
        except Exception as e:
            print(f"   ⚠️  โหลด GIF ไม่ได้ ({path}): {e}")
            return None

        frames: List[Tuple[np.ndarray, float]] = []

        try:
            while True:
                # duration ต่อ frame (ms → sec), default 100ms ถ้าไม่ระบุ
                dur_ms  = pil_gif.info.get("duration", 100)
                dur_sec = max(dur_ms, 10) / 1000.0  # ป้องกัน duration = 0

                # แปลงเป็น RGBA เพื่อรักษา transparency
                rgba = pil_gif.convert("RGBA")

                # resize ด้วย Pillow (LANCZOS คุณภาพดี)
                rgba = rgba.resize(size, Image.LANCZOS)

                arr = np.array(rgba, dtype=np.uint8)  # (H, W, 4) RGBA

                # แปลง RGBA → BGRA (OpenCV ใช้ BGR)
                bgra = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)

                frames.append((bgra, dur_sec))
                pil_gif.seek(pil_gif.tell() + 1)

        except EOFError:
            pass  # อ่านครบทุก frame แล้ว
        except Exception as e:
            print(f"   ⚠️  อ่าน GIF frame ไม่สำเร็จ ({path}): {e}")
            if not frames:
                return None

        if not frames:
            return None

        n = len(frames)
        total_ms = sum(d * 1000 for _, d in frames)
        print(f"   🎞️  โหลด GIF สำเร็จ: {os.path.basename(path)} "
              f"({n} frames, {total_ms:.0f}ms)")
        return frames

    # ------------------------------------------------------------------
    # Static image support (PNG / JPG)
    # ------------------------------------------------------------------

    def _load_meme(
        self, path: str, size: Tuple[int, int]
    ) -> Optional[np.ndarray]:
        """
        โหลดและ resize ภาพนิ่ง (PNG / JPG)

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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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
        alpha    = meme[:, :, 3:4].astype(np.float32) / 255.0  # (H, W, 1)
        meme_bgr = meme[:, :, :3].astype(np.float32)
        roi_f    = roi.astype(np.float32)

        blended = alpha * meme_bgr + (1.0 - alpha) * roi_f
        roi[:] = blended.astype(np.uint8)


# ทดสอบโมดูลเดี่ยว
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.camera import Camera

    print("🧪 ทดสอบ MemeOverlay (รวม GIF)")
    print("วางภาพ/GIF ทดสอบลงใน memes/neutral/ ก่อนรัน")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_dir = os.path.join(base_dir, "memes", "neutral")
    test_files = [
        os.path.join(test_dir, f)
        for f in os.listdir(test_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ] if os.path.isdir(test_dir) else []

    camera  = Camera(camera_id=0, width=640, height=480)
    overlay = MemeOverlay()

    print(f"พบไฟล์ทดสอบ: {len(test_files)} ไฟล์")
    for f in test_files:
        print(f"  - {os.path.basename(f)}")

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

"""
Meme Selector Module - เลือก Meme ตามท่าทางที่ตรวจจับได้
รับผิดชอบ: map expression/gesture → path ไฟล์ Meme, cooldown, random selection
"""

import os
import json
import random
import time
from typing import Optional


class MemeSelector:
    """
    เลือก Meme จากโฟลเดอร์ตามท่าทางที่ตรวจจับได้

    Args:
        meme_dir: โฟลเดอร์หลักที่เก็บ Meme (default: "memes/")
        mapping_path: path ไปยัง meme_mapping.json
        cooldown_sec: เวลาขั้นต่ำ (วินาที) ก่อนเปลี่ยน Meme ใหม่ (default: 2.0)
    """

    SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

    def __init__(
        self,
        meme_dir: str = "memes/",
        mapping_path: str = "config/meme_mapping.json",
        cooldown_sec: float = 2.0,
    ):
        self.cooldown_sec = cooldown_sec

        # หา absolute path ของ meme_dir
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.meme_dir = os.path.join(base, meme_dir) if not os.path.isabs(meme_dir) else meme_dir

        # โหลด mapping
        self._mapping = self._load_mapping(os.path.join(base, mapping_path))

        # Cache รายการไฟล์ทุกหมวด (โหลดครั้งเดียว)
        self._cache: dict[str, list[str]] = {}
        self._build_cache()

        # State
        self._current_expression: Optional[str] = None
        self._current_meme_path: Optional[str]  = None
        self._last_change_time: float = 0.0

        print(f"🖼️  MemeSelector เริ่มต้นสำเร็จ (meme_dir: {self.meme_dir})")
        self._print_stats()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _load_mapping(self, path: str) -> dict:
        """โหลด meme_mapping.json"""
        if not os.path.isfile(path):
            path = "config/meme_mapping.json"  # fallback relative

        try:
            with open(path, "r", encoding="utf-8") as f:
                mapping = json.load(f)
            print(f"   โหลด meme mapping จาก {path}")
            return mapping
        except Exception as e:
            print(f"   ⚠️  โหลด mapping ไม่ได้ ({e}) ใช้ default")
            return {
                "surprised": "surprised",
                "happy":     "happy",
                "angry":     "angry",
                "sleepy":    "sleepy",
                "thinking":  "thinking",
                "thumbs_up": "thumbs_up",
                "peace":     "peace",
                "neutral":   "neutral",
                "pointing":  "neutral",
                "fist":      "neutral",
            }

    def _build_cache(self) -> None:
        """สร้าง cache รายการไฟล์ Meme ทุกหมวด"""
        if not os.path.isdir(self.meme_dir):
            print(f"   ⚠️  ไม่พบโฟลเดอร์ {self.meme_dir}")
            return

        for folder_name in os.listdir(self.meme_dir):
            folder_path = os.path.join(self.meme_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith(self.SUPPORTED_EXTS)
            ]
            self._cache[folder_name] = files

    def _print_stats(self) -> None:
        """แสดงสถิติ Meme ที่โหลดได้"""
        total = sum(len(v) for v in self._cache.values())
        if total == 0:
            print("   ⚠️  ไม่พบไฟล์ Meme — กรุณาเพิ่มภาพลงในโฟลเดอร์ memes/")
        else:
            print(f"   พบ Meme ทั้งหมด {total} ไฟล์ ใน {len(self._cache)} หมวด")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def select_meme(self, expression: str) -> Optional[str]:
        """
        เลือก path ไฟล์ Meme สำหรับ expression ที่กำหนด

        - ถ้า expression เปลี่ยน → เลือก Meme ใหม่ทันที
        - ถ้า expression เดิมแต่หมด cooldown → เลือก Meme ใหม่ใน category เดิม
        - ถ้ายังอยู่ใน cooldown → คืน Meme เดิม

        Args:
            expression: ชื่อท่าทาง เช่น "happy", "thumbs_up"

        Returns:
            str path ของไฟล์ Meme หรือ None ถ้าไม่มีไฟล์
        """
        now = time.time()
        expression_changed = expression != self._current_expression
        cooldown_expired   = (now - self._last_change_time) >= self.cooldown_sec

        if expression_changed or cooldown_expired or self._current_meme_path is None:
            new_path = self._pick_random(expression)
            if new_path:
                self._current_expression  = expression
                self._current_meme_path   = new_path
                self._last_change_time    = now

        return self._current_meme_path

    def force_next(self) -> Optional[str]:
        """
        บังคับเปลี่ยน Meme ทันที (เช่น เมื่อผู้ใช้กดปุ่ม)

        Returns:
            str path ของ Meme ใหม่ หรือ None
        """
        self._last_change_time = 0  # reset cooldown
        return self.select_meme(self._current_expression or "neutral")

    def reload_cache(self) -> None:
        """โหลด cache ใหม่ (ใช้เมื่อเพิ่ม/ลบ Meme ขณะรันโปรแกรม)"""
        self._cache.clear()
        self._build_cache()
        print("🔄 โหลด Meme cache ใหม่แล้ว")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _pick_random(self, expression: str) -> Optional[str]:
        """เลือก Meme แบบสุ่มจาก category ของ expression"""
        folder_name = self._mapping.get(expression, "neutral")
        candidates  = self._cache.get(folder_name, [])

        if not candidates:
            # fallback → neutral
            candidates = self._cache.get("neutral", [])

        if not candidates:
            return None

        # หลีกเลี่ยง Meme เดิมถ้ามีตัวเลือกอื่น
        if len(candidates) > 1 and self._current_meme_path in candidates:
            candidates = [c for c in candidates if c != self._current_meme_path]

        return random.choice(candidates)


# ทดสอบโมดูลเดี่ยว
if __name__ == "__main__":
    selector = MemeSelector()

    expressions = ["surprised", "happy", "angry", "sleepy",
                   "thinking", "thumbs_up", "peace", "neutral"]

    for expr in expressions:
        path = selector.select_meme(expr)
        print(f"  {expr:12s} → {path or '(ไม่มีไฟล์)'}")

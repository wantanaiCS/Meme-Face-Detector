"""
Display Module - จัดการการแสดงผลสำหรับ Meme Face Detector
รับผิดชอบ: แสดงผลบนหน้าจอ, จัดการ keyboard input
"""

import cv2
from typing import Optional, Tuple
import numpy as np
import time


class Display:
    """
    Display manager class สำหรับจัดการการแสดงผล GUI
    
    Args:
        window_name: ชื่อหน้าต่าง (default: "Meme Face Detector")
        show_fps: แสดง FPS บนหน้าจอหรือไม่ (default: True)
    """
    
    def __init__(
        self, 
        window_name: str = "Meme Face Detector",
        show_fps: bool = True
    ):
        self.window_name = window_name
        self.show_fps = show_fps
        self._is_created = False
        
        # FPS calculation
        self._prev_time = time.time()
        self._fps = 0.0
        self._frame_count = 0
        
        # Exit keys
        self._exit_keys = (ord('q'), ord('Q'), 27)  # Q, q, ESC
        
        self._create_window()
    
    def _create_window(self) -> None:
        """สร้างหน้าต่างแสดงผล"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self._is_created = True
        print(f"🖥️ สร้างหน้าต่าง '{self.window_name}' เรียบร้อย")
    
    def show(self, frame: np.ndarray) -> None:
        """
        แสดง frame บนหน้าต่าง
        
        Args:
            frame: ภาพที่จะแสดง (numpy.ndarray)
        """
        if frame is None:
            return
        
        # คำนวณ FPS
        self._calculate_fps()
        
        # วาด FPS บนภาพ
        if self.show_fps and self._fps > 0:
            self._draw_fps(frame)
        
        # แสดงภาพ
        cv2.imshow(self.window_name, frame)
    
    def _calculate_fps(self) -> None:
        """คำนวณ FPS"""
        self._frame_count += 1
        current_time = time.time()
        
        # คำนวณทุก 30 frames
        if self._frame_count >= 30:
            elapsed = current_time - self._prev_time
            if elapsed > 0:
                self._fps = self._frame_count / elapsed
            
            self._frame_count = 0
            self._prev_time = current_time
    
    def _draw_fps(self, frame: np.ndarray) -> None:
        """
        วาด FPS บนภาพ
        
        Args:
            frame: ภาพที่จะวาด
        """
        fps_text = f"FPS: {self._fps:.1f}"
        
        # กำหนดตำแหน่ง (ซ้ายบน)
        position = (10, 30)
        
        # วาดเงาใต้ตัวอักษรเพื่อให้อ่านง่าย
        cv2.putText(
            frame, fps_text, 
            (position[0] + 2, position[1] + 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0, 0, 0), 2, cv2.LINE_AA
        )
        
        # วาดตัวอักษร
        cv2.putText(
            frame, fps_text, position,
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0, 255, 0), 2, cv2.LINE_AA
        )
    
    def should_exit(self) -> bool:
        """
        ตรวจสอบว่าผู้ใช้กดปุ่มออกหรือไม่
        
        Returns:
            bool: True ถ้าควรออก, False ถ้ายังไม่ต้องออก
        """
        key = cv2.waitKey(1) & 0xFF
        return key in self._exit_keys
    
    def wait_key(self, delay: int = 1) -> int:
        """
        รอรับ key press
        
        Args:
            delay: เวลารอในมิลลิวินาที (default: 1)
            
        Returns:
            int: ค่า ASCII ของปุ่มที่กด, หรือ -1 ถ้าไม่มีปุ่มถูกกด
        """
        return cv2.waitKey(delay) & 0xFF
    
    def draw_text(
        self, 
        frame: np.ndarray, 
        text: str, 
        position: Tuple[int, int] = (10, 50),
        font_scale: float = 0.7,
        color: Tuple[int, int, int] = (255, 255, 255),
        thickness: int = 2
    ) -> np.ndarray:
        """
        วาดข้อความบนภาพ
        
        Args:
            frame: ภาพที่จะวาด
            text: ข้อความที่จะวาด
            position: ตำแหน่ง (x, y)
            font_scale: ขนาดฟอนต์
            color: สี (B, G, R)
            thickness: ความหนา
            
        Returns:
            numpy.ndarray: ภาพที่วาดแล้ว
        """
        # วาดเงา
        cv2.putText(
            frame, text,
            (position[0] + 2, position[1] + 2),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
            (0, 0, 0), thickness + 1, cv2.LINE_AA
        )
        
        # วาดตัวอักษร
        cv2.putText(
            frame, text, position,
            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
            color, thickness, cv2.LINE_AA
        )
        
        return frame
    
    def draw_status(
        self, 
        frame: np.ndarray, 
        expression: str,
        gesture: Optional[str] = None
    ) -> np.ndarray:
        """
        วาดสถานะ expression/gesture บนภาพ
        
        Args:
            frame: ภาพที่จะวาด
            expression: ชื่อ expression
            gesture: ชื่อ gesture (optional)
            
        Returns:
            numpy.ndarray: ภาพที่วาดแล้ว
        """
        h, w = frame.shape[:2]
        
        # สร้าง status text
        status = gesture if gesture else expression
        
        # วาดกล่องด้านล่าง
        box_height = 50
        cv2.rectangle(
            frame, 
            (0, h - box_height), 
            (w, h),
            (0, 0, 0), 
            cv2.FILLED
        )
        
        # วาดข้อความ
        cv2.putText(
            frame, f"Expression: {expression}",
            (10, h - 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (255, 255, 255), 2, cv2.LINE_AA
        )
        
        if gesture:
            cv2.putText(
                frame, f"Gesture: {gesture}",
                (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 255, 255), 2, cv2.LINE_AA
            )
        
        return frame
    
    def close(self) -> None:
        """ปิดหน้าต่างและคืนทรัพยากร"""
        cv2.destroyWindow(self.window_name)
        self._is_created = False
        print("🖥️ ปิดหน้าต่างเรียบร้อย")
    
    def close_all(self) -> None:
        """ปิดทุกหน้าต่าง"""
        cv2.destroyAllWindows()
        self._is_created = False
        print("🖥️ ปิดทุกหน้าต่างเรียบร้อย")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()
        return False


# สำหรับทดสอบโมดูล
if __name__ == "__main__":
    print("🧪 ทดสอบ Display Module")
    
    # สร้าง test frame
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    test_frame[:] = (100, 100, 100)  # สีเทา
    
    with Display(window_name="Display Test", show_fps=True) as display:
        print("กด 'Q' เพื่อออก")
        
        frame_count = 0
        while True:
            # สร้าง frame copy
            frame = test_frame.copy()
            
            # วาดข้อความทดสอบ
            display.draw_text(frame, "Display Module Test", position=(10, 100))
            display.draw_status(frame, expression="neutral", gesture=None)
            
            # แสดง frame
            display.show(frame)
            
            if display.should_exit():
                break
            
            frame_count += 1
    
    print("✅ ทดสอบเสร็จสิ้น")

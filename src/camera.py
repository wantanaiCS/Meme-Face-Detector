"""
Camera Module - จัดการกล้องสำหรับ Meme Face Detector
รับผิดชอบ: เปิดกล้อง, อ่าน frame, ปิดกล้อง
"""

import cv2
from typing import Optional, Tuple
import numpy as np


class Camera:
    """
    Camera manager class สำหรับจัดการการเข้าถึงกล้อง
    
    Args:
        camera_id: ID ของกล้อง (default: 0)
        width: ความกว้างของ frame (default: 1280)
        height: ความสูงของ frame (default: 720)
        mirror: กลับภาพซ้าย-ขวาหรือไม่ (default: True)
    """
    
    def __init__(
        self, 
        camera_id: int = 0, 
        width: int = 1280, 
        height: int = 720,
        mirror: bool = True
    ):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.mirror = mirror
        self.cap: Optional[cv2.VideoCapture] = None
        self._is_opened = False
        
        self._open_camera()
    
    def _open_camera(self) -> bool:
        """
        เปิดกล้องและตั้งค่าความละเอียด
        
        Returns:
            bool: True ถ้าเปิดสำเร็จ, False ถ้าไม่สำเร็จ
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"❌ ไม่สามารถเปิดกล้อง ID {self.camera_id} ได้")
                return False
            
            # ตั้งค่าความละเอียด
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # ตรวจสอบความละเอียดจริงที่กล้องรองรับ
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"📷 กล้องเปิดสำเร็จ: {actual_width:.0f}x{actual_height:.0f} @ {actual_fps:.0f}fps")
            
            self._is_opened = True
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการเปิดกล้อง: {e}")
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        อ่าน frame จากกล้อง
        
        Returns:
            numpy.ndarray หรือ None: frame ที่อ่านได้, หรือ None ถ้าไม่สำเร็จ
        """
        if not self._is_opened or self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            return None
        
        # กลับภาพซ้าย-ขวา (mirror effect) เพื่อให้เหมือนกระจก
        if self.mirror:
            frame = cv2.flip(frame, 1)
        
        return frame
    
    def get_frame_shape(self) -> Optional[Tuple[int, int, int]]:
        """
        ได้ขนาดของ frame
        
        Returns:
            tuple: (height, width, channels) หรือ None
        """
        if not self._is_opened or self.cap is None:
            return None
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        return (height, width, 3)
    
    def is_opened(self) -> bool:
        """ตรวจสอบว่ากล้องเปิดอยู่หรือไม่"""
        return self._is_opened and self.cap is not None and self.cap.isOpened()
    
    def release(self) -> None:
        """ปิดกล้องและคืนทรัพยากร"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self._is_opened = False
            print("📷 ปิดกล้องเรียบร้อย")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ปิดกล้องอัตโนมัติ"""
        self.release()
        return False
    
    def __del__(self):
        """Destructor - ปิดกล้องเมื่อ object ถูกทำลาย"""
        self.release()


# สำหรับทดสอบโมดูล
if __name__ == "__main__":
    print("🧪 ทดสอบ Camera Module")
    
    with Camera(camera_id=0, width=640, height=480) as camera:
        if not camera.is_opened():
            print("❌ ไม่สามารถเปิดกล้องได้")
            exit(1)
        
        print("กด 'Q' เพื่อออก")
        
        while True:
            frame = camera.read_frame()
            if frame is None:
                print("❌ อ่าน frame ไม่ได้")
                break
            
            cv2.imshow("Camera Test", frame)
            
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), 27):
                break
    
    cv2.destroyAllWindows()
    print("✅ ทดสอบเสร็จสิ้น")

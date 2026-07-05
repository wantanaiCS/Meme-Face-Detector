#!/usr/bin/env python3
"""
Meme Face Detector - Entry Point
ระบบตรวจจับลักษณะท่าทางและสีหน้าผ่านกล้อง แล้วแสดงภาพ Meme ตลก ๆ แบบ Real-time

การใช้งาน:
    python main.py [--debug] [--camera ID] [--width W] [--height H]

การควบคุม:
    Q / ESC  — ออกจากโปรแกรม
    D        — toggle debug landmarks
    N        — เปลี่ยน Meme ใหม่ทันที (next meme)
"""

import sys
import os
import argparse
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.camera            import Camera
from src.detector          import FaceDetector
from src.expression_analyzer import ExpressionAnalyzer
from src.meme_selector     import MemeSelector
from src.overlay           import MemeOverlay
from src.display           import Display


# ------------------------------------------------------------------
# CLI arguments
# ------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Meme Face Detector")
    parser.add_argument("--debug",  action="store_true",
                        help="แสดง landmarks บนหน้าจอ")
    parser.add_argument("--camera", type=int, default=0,
                        help="Camera ID (default: 0)")
    parser.add_argument("--width",  type=int, default=1280,
                        help="ความกว้าง frame (default: 1280)")
    parser.add_argument("--height", type=int, default=720,
                        help="ความสูง frame (default: 720)")
    return parser.parse_args()


# ------------------------------------------------------------------
# HUD helpers
# ------------------------------------------------------------------

def draw_hud(
    frame,
    expression: str,
    gesture,
    debug_values: dict,
    show_debug: bool,
) -> None:
    """วาดข้อมูลสถานะมุมซ้ายล่าง"""
    h, w = frame.shape[:2]
    state = gesture if gesture else expression
    emoji_map = {
        # face expressions
        "laughing":      "🤣",
        "wink":          "😉",
        "derp":          "😛",
        "rage":          "🤬",
        "sigma":         "😏",
        "confused":      "😕",
        "sad":           "😢",
        "surprised":     "😮",
        "happy":         "😄",
        "angry":         "😠",
        "sleepy":        "😴",
        "thinking":      "🤔",
        "neutral":       "😐",
        # hand gestures
        "middle_finger": "🖕",
        "ok_sign":       "👌",
        "thumbs_up":     "👍",
        "peace":         "✌️",
        "pointing":      "☝️",
        "fist":          "✊",
    }
    label = f"{emoji_map.get(state, '')} {state.upper()}"

    # กล่องพื้นหลัง
    box_h = 95 if show_debug else 50
    cv2.rectangle(frame, (0, h - box_h), (w, h), (0, 0, 0), cv2.FILLED)

    # Expression / Gesture
    cv2.putText(frame, f"Expression: {expression}", (10, h - box_h + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    if gesture:
        cv2.putText(frame, f"Gesture: {gesture}", (10, h - box_h + 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)

    # Debug values — แสดงเป็น overlay กล่องใสมุมซ้ายบน (ไม่ชนกับ HUD ล่าง)
    if show_debug and debug_values:
        items  = list(debug_values.items())
        cols   = 3                      # 3 คอลัมน์
        col_w  = max(w // cols, 200)    # ความกว้างแต่ละคอลัมน์
        row_h  = 20                     # ความสูงแต่ละแถว
        rows   = (len(items) + cols - 1) // cols
        pad    = 8
        box_h  = rows * row_h + pad * 2
        box_y  = 45                     # เว้นจาก FPS counter

        # พื้นหลังโปร่งแสง
        overlay_bg = frame[box_y:box_y + box_h, 0:col_w * cols].copy()
        cv2.rectangle(frame, (0, box_y), (col_w * cols, box_y + box_h),
                      (0, 0, 0), cv2.FILLED)
        cv2.addWeighted(overlay_bg, 0.35,
                        frame[box_y:box_y + box_h, 0:col_w * cols], 0.65,
                        0, frame[box_y:box_y + box_h, 0:col_w * cols])

        for i, (k, v) in enumerate(items):
            col = i % cols
            row = i // cols
            tx  = col * col_w + pad
            ty  = box_y + pad + row * row_h + 13
            # highlight ค่าที่สูง (> 0.15) ด้วยสีเหลือง
            color = (0, 255, 255) if float(v) > 0.15 else (160, 160, 160)
            cv2.putText(frame, f"{k}: {v}", (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)


def draw_controls_hint(frame) -> None:
    """วาดคำแนะนำปุ่มมุมขวาบน"""
    h, w = frame.shape[:2]
    hints = ["[Q/ESC] ออก", "[D] Debug", "[N] Next Meme"]
    for i, hint in enumerate(hints):
        x = w - 160
        y = 25 + i * 22
        cv2.putText(frame, hint, (x + 1, y + 1),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, hint, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main() -> int:
    args = parse_args()

    print("=" * 55)
    print("🎭  Meme Face Detector")
    print("    Real-time expression → meme overlay")
    print("=" * 55)
    print()

    # ---- Init components ----
    print("🔧 กำลังเริ่มต้นระบบ...")
    show_debug = args.debug

    try:
        camera   = Camera(
            camera_id=args.camera,
            width=args.width,
            height=args.height,
            mirror=True,
        )
        detector = FaceDetector(draw_landmarks=show_debug)
        analyzer = ExpressionAnalyzer()
        selector = MemeSelector()
        overlay  = MemeOverlay()
        display  = Display(window_name="Meme Face Detector", show_fps=True)

        if not camera.is_opened():
            print("❌ ไม่สามารถเปิดกล้องได้")
            return 1

        print()
        print("🎬 เริ่มทำงานแล้ว!")
        print("   [Q / ESC]  ออก")
        print("   [D]        toggle debug landmarks")
        print("   [N]        เปลี่ยน Meme ใหม่ทันที")
        print("-" * 55)

        # ---- Main loop ----
        while True:
            # 1. อ่าน frame
            frame = camera.read_frame()
            if frame is None:
                print("⚠️  อ่าน frame ไม่สำเร็จ")
                continue

            # 2. ตรวจจับ (ใช้ detect_all เพื่อแชร์ RGB conversion)
            detector.draw_landmarks = show_debug
            face_lm, hand_lm = detector.detect_all(frame)

            # 3. วิเคราะห์
            expression  = analyzer.analyze_expression(face_lm, frame.shape)
            gesture     = analyzer.analyze_gesture(hand_lm, frame.shape)
            debug_vals  = analyzer.get_debug_values(face_lm, frame.shape) if show_debug else {}

            # 4. เลือก Meme (gesture มี priority สูงกว่า expression)
            active_state = gesture if gesture else expression
            meme_path    = selector.select_meme(active_state) if active_state != "neutral" else None

            # 5. วาง Meme overlay (ไม่แสดงเมื่อ neutral)
            if meme_path:
                overlay.apply(frame, meme_path, position="top_right", size=(260, 260))

            # 6. วาด HUD + hints
            draw_hud(frame, expression, gesture, debug_vals, show_debug)
            draw_controls_hint(frame)

            # 7. แสดงผล
            display.show(frame)

            # 8. Keyboard input
            key = display.wait_key(1)
            if key in (ord("q"), ord("Q"), 27):
                print("\n🛑 ผู้ใช้กดออก")
                break
            elif key in (ord("d"), ord("D")):
                show_debug = not show_debug
                print(f"🐛 Debug mode: {'ON' if show_debug else 'OFF'}")
            elif key in (ord("n"), ord("N")):
                new_path = selector.force_next()
                print(f"⏭️  Next meme: {os.path.basename(new_path) if new_path else 'ไม่มี'}")

    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C")

    except Exception as e:
        import traceback
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        traceback.print_exc()
        return 1

    finally:
        print("\n🔧 กำลังปิดระบบ...")
        for obj_name in ("display", "detector", "camera"):
            obj = locals().get(obj_name)
            if obj is None:
                continue
            try:
                if obj_name == "display":
                    obj.close_all()
                else:
                    obj.release()
            except Exception:
                pass
        print("✅ ปิดระบบเรียบร้อย")
        print("\nขอบคุณที่ใช้งาน Meme Face Detector! 👋")

    return 0


if __name__ == "__main__":
    sys.exit(main())

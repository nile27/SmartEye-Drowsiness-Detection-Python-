import cv2
import numpy as np
import time

class OverlayRenderer:
    """Renders state text, eye contours, values, and visual alert overlays on camera frames."""
    
    # State-based Color mappings (BGR format)
    COLORS = {
        "Awake": (0, 220, 0),       # Vibrant Green
        "Drowsy": (0, 200, 255),    # Amber/Yellow-Orange
        "Sleeping": (0, 0, 255),    # Bright Red
        "Calibrating": (255, 200, 0) # Cyan/Light Blue
    }

    def draw_status(self, 
                    frame: np.ndarray, 
                    state: str, 
                    ear: float, 
                    threshold: float, 
                    fps: float, 
                    calibration_progress: float = 0.0) -> np.ndarray:
        """Draws state information, EAR values, and FPS onto the frame."""
        h, w, _ = frame.shape
        color = self.COLORS.get(state, (255, 255, 255))
        
        # 1. Draw semi-transparent header bar for dashboard feel
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 65), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # 2. Render State Text
        state_label = f"STATE: {state.upper()}"
        if state == "Calibrating":
            state_label += f" ({calibration_progress:.0f}%)"
            
        cv2.putText(frame, state_label, (20, 42), cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2, cv2.LINE_AA)
        
        # 3. Render EAR values and Threshold
        ear_text = f"EAR: {ear:.3f} | THRESHOLD: {threshold:.3f}"
        cv2.putText(frame, ear_text, (w - 380, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1, cv2.LINE_AA)
        
        # Draw EAR visual progress bar
        bar_x = w - 380
        bar_y = 38
        bar_w = 200
        bar_h = 10
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        
        # Filled bar based on EAR (max displayable EAR = 0.4)
        fill_ratio = min(ear / 0.4, 1.0)
        fill_w = int(bar_w * fill_ratio)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)
        
        # Draw threshold marker on EAR bar
        th_pos = int(bar_w * (threshold / 0.4))
        if 0 < th_pos < bar_w:
            cv2.line(frame, (bar_x + th_pos, bar_y - 2), (bar_x + th_pos, bar_y + bar_h + 2), (255, 255, 255), 2)
            
        # 4. Render FPS (bottom right)
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(frame, fps_text, (w - 90, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
        
        return frame

    def draw_eye_contours(self, frame: np.ndarray, eye_pts: dict[str, list[tuple[int, int]]], state: str) -> np.ndarray:
        """Draws contour lines and landmark points around the eyes."""
        color = self.COLORS.get(state, (255, 255, 255))
        
        for eye_side in ["left", "right"]:
            pts = eye_pts.get(eye_side, [])
            if not pts or len(pts) < 6:
                continue
                
            # Draw contour lines: p1 -> p2 -> p3 -> p4 -> p5 -> p6 -> p1
            contour = np.array(pts, dtype=np.int32)
            cv2.polylines(frame, [contour], isClosed=True, color=color, thickness=1, lineType=cv2.LINE_AA)
            
            # Draw eye keypoints
            for pt in pts:
                cv2.circle(frame, pt, 2, (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, pt, 3, color, 1, cv2.LINE_AA)
                
        return frame

    def draw_alert_border(self, frame: np.ndarray, state: str) -> np.ndarray:
        """Draws a blinking red border around the frame for critical Sleeping alert."""
        h, w, _ = frame.shape
        
        if state == "Sleeping":
            # Blinking at 4Hz (every 250ms)
            if int(time.time() * 4) % 2 == 0:
                # Outer red frame border
                cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 12)
                
                # Render dramatic text center-screen
                warn_text = "WARNING: SLEEPING DETECTED"
                text_sz = cv2.getTextSize(warn_text, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
                tx = (w - text_sz[0]) // 2
                ty = (h + text_sz[1]) // 2
                
                # Semi-transparent background box behind text
                cv2.rectangle(frame, (tx - 15, ty - text_sz[1] - 15), (tx + text_sz[0] + 15, ty + 15), (0, 0, 0), -1)
                cv2.putText(frame, warn_text, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
                
        elif state == "Drowsy":
            # Milder solid yellow border
            cv2.rectangle(frame, (0, 0), (w, h), (0, 200, 255), 6)
            
        return frame

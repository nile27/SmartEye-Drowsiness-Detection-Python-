# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import mediapipe as mp
# pyrefly: ignore [missing-import]
import numpy as np
import logging

logger = logging.getLogger("SmartEye.FaceDetector")

class FaceDetector:
    """Uses MediaPipe Face Mesh to detect facial landmarks and extract eye regions."""
    
    # Anatomical Right Eye Indices
    # p1: inner corner, p2/p3: top, p4: outer corner, p5/p6: bottom
    RIGHT_EYE_INDICES = [133, 160, 159, 33, 145, 153]
    
    # Anatomical Left Eye Indices
    # p1: inner corner, p2/p3: top, p4: outer corner, p5/p6: bottom
    LEFT_EYE_INDICES = [362, 385, 386, 263, 374, 380]

    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def detect_landmarks(self, frame: np.ndarray) -> list | None:
        """Processes the frame and extracts normalized landmark coordinates.
        
        Args:
            frame: Input BGR image from camera.
            
        Returns:
            List of normalized landmarks, or None if no face is detected.
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
            
        return results.multi_face_landmarks[0].landmark

    def get_eye_landmarks(self, landmarks, img_w: int, img_h: int) -> dict[str, list[tuple[int, int]]]:
        """Extracts pixel coordinates for both eyes from normalized landmarks.
        
        Returns:
            Dictionary containing 'left' and 'right' lists of (x, y) coordinates.
        """
        left_eye_pts = []
        right_eye_pts = []
        
        # Convert normalized coordinates to pixel values
        for idx in self.LEFT_EYE_INDICES:
            lm = landmarks[idx]
            x, y = int(lm.x * img_w), int(lm.y * img_h)
            left_eye_pts.append((x, y))
            
        for idx in self.RIGHT_EYE_INDICES:
            lm = landmarks[idx]
            x, y = int(lm.x * img_w), int(lm.y * img_h)
            right_eye_pts.append((x, y))
            
        return {
            "left": left_eye_pts,
            "right": right_eye_pts
        }
        
    def close(self):
        """Closes the face mesh model."""
        self.face_mesh.close()

# pyrefly: ignore [missing-import]
import cv2
import logging

logger = logging.getLogger("SmartEye.CameraManager")

class CameraManager:
    """Manages the webcam frame capture and OpenCV camera device lifecycle."""
    
    def __init__(self, device_index: int = 0, width: int = 640, height: int = 480):
        self.device_index = device_index
        self.width = width
        self.height = height
        self.cap = None

    def initialize_camera(self) -> bool:
        """Initializes the camera capture device."""
        logger.info(f"Initializing camera device {self.device_index}...")
        self.cap = cv2.VideoCapture(self.device_index)
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera device {self.device_index}.")
            return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.info(f"Camera initialized successfully. Resolution: {actual_width}x{actual_height}")
        return True

    def get_frame(self) -> tuple[bool, cv2.typing.MatLike | None]:
        """Captures a single frame from the camera.
        
        Returns:
            Tuple[bool, np.ndarray]: (Success status, BGR image frame)
        """
        if self.cap is None or not self.cap.isOpened():
            logger.warning("Camera is not initialized.")
            return False, None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to grab frame from camera.")
            return False, None
            
        return True, frame

    def release(self):
        """Releases the camera resource."""
        if self.cap is not None:
            logger.info("Releasing camera device...")
            self.cap.release()
            self.cap = None
            logger.info("Camera released.")

import time
from collections import deque
import logging

logger = logging.getLogger("SmartEye.DrowsinessClassifier")

class DrowsinessClassifier:
    """Classifies user state (Awake, Drowsy, Sleeping) based on smoothed EAR and time thresholds."""
    
    def __init__(self, 
                 initial_threshold: float = 0.22, 
                 drowsy_time_threshold: float = 1.0, 
                 sleeping_time_threshold: float = 3.0,
                 smoothing_window: int = 5):
        self.threshold = initial_threshold
        self.drowsy_time_threshold = drowsy_time_threshold
        self.sleeping_time_threshold = sleeping_time_threshold
        self.smoothing_window = smoothing_window
        
        # EAR sliding buffer for temporal smoothing
        self.ear_history = deque(maxlen=smoothing_window)
        
        # State tracking
        self.state = "Awake"
        self.closed_start_time = None
        
        # Calibration state
        self.is_calibrated = False
        self.calibration_ear_values = []

    def update(self, raw_ear: float) -> tuple[str, float]:
        """Updates the classifier with a new raw EAR measurement.
        
        Returns:
            Tuple[str, float]: (State string, Smoothed EAR value)
        """
        # Temporal smoothing (Moving Average)
        self.ear_history.append(raw_ear)
        smoothed_ear = sum(self.ear_history) / len(self.ear_history)
        
        # If in calibration phase, skip state classification
        if not self.is_calibrated:
            return "Calibrating", smoothed_ear
            
        # Determine eye state (open vs closed) based on threshold
        if smoothed_ear < self.threshold:
            if self.closed_start_time is None:
                self.closed_start_time = time.time()
                
            elapsed_time = time.time() - self.closed_start_time
            
            if elapsed_time >= self.sleeping_time_threshold:
                self.state = "Sleeping"
            elif elapsed_time >= self.drowsy_time_threshold:
                self.state = "Drowsy"
            else:
                # Eyes closed, but below duration threshold to trigger warning
                self.state = "Awake"
        else:
            # Eyes are open, reset timer and state to Awake
            self.closed_start_time = None
            self.state = "Awake"
            
        return self.state, smoothed_ear

    def start_calibration(self):
        """Resets calibration state to begin collecting new data."""
        self.is_calibrated = False
        self.calibration_ear_values = []
        logger.info("Starting calibration session...")

    def collect_calibration_ear(self, raw_ear: float):
        """Collects raw EAR values during the calibration phase."""
        self.calibration_ear_values.append(raw_ear)

    def finalize_calibration(self, threshold_ratio: float = 0.75, min_threshold: float = 0.19):
        """Calculates the customized threshold based on collected calibration EARs.
        
        Uses threshold_ratio of the average EAR value as the new threshold, clamped to a minimum.
        """
        if not self.calibration_ear_values:
            logger.warning("No calibration data collected. Using default threshold.")
            self.is_calibrated = True
            return
            
        avg_base_ear = sum(self.calibration_ear_values) / len(self.calibration_ear_values)
        self.threshold = max(avg_base_ear * threshold_ratio, min_threshold)
        self.is_calibrated = True
        logger.info(f"Calibration complete. Base EAR: {avg_base_ear:.3f}, New Threshold: {self.threshold:.3f}")
        
    def reset(self):
        """Resets classifier state."""
        self.ear_history.clear()
        self.closed_start_time = None
        self.state = "Awake"

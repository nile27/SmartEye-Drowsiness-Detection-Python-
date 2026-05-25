import os

# Camera Settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_FPS = 30

# EAR Thresholds & Timing (seconds)
DEFAULT_EAR_THRESHOLD = 0.22
DROWSY_TIME_THRESHOLD = 1.0
SLEEPING_TIME_THRESHOLD = 3.0

# Calibration Settings
CALIBRATION_DURATION = 5.0  # Duration in seconds to calibrate base EAR
CALIBRATION_THRESHOLD_RATIO = 0.89  # Sensitivity: ratio of base EAR to set as threshold (e.g. 0.85). Higher = more sensitive.
MIN_EAR_THRESHOLD = 0.18  # Minimum absolute EAR threshold value to maintain sensitivity if calibration EAR is too low.

# Smoothing Configuration
EAR_SMOOTHING_WINDOW = 5  # Number of frames for moving average

# Logs Settings
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Audio Settings
# We will use macOS default system sounds or simple audio alerts if custom wav not present
ALERT_SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "alert.wav")

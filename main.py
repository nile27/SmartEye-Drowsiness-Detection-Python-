# pyrefly: ignore [missing-import]
import cv2
import time
import logging
import sys
import os

import config
from src.camera import CameraManager
from src.detector import FaceDetector
from src.analyzer import EyeAnalyzer
from src.classifier import DrowsinessClassifier
from src.alert import AlertManager
from src.renderer import OverlayRenderer
from src.utils.logger import SessionLogger

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SmartEye")

def main():
    logger.info("Starting SmartEye Application...")
    
    # Initialize components
    camera = CameraManager(
        device_index=config.CAMERA_INDEX,
        width=config.CAMERA_WIDTH,
        height=config.CAMERA_HEIGHT
    )
    detector = FaceDetector()
    analyzer = EyeAnalyzer()
    classifier = DrowsinessClassifier(
        initial_threshold=config.DEFAULT_EAR_THRESHOLD,
        drowsy_time_threshold=config.DROWSY_TIME_THRESHOLD,
        sleeping_time_threshold=config.SLEEPING_TIME_THRESHOLD,
        smoothing_window=config.EAR_SMOOTHING_WINDOW
    )
    alert_manager = AlertManager(alert_sound_path=config.ALERT_SOUND_PATH)
    renderer = OverlayRenderer()
    session_logger = SessionLogger(log_dir=config.LOG_DIR)
    
    # Initialize camera device
    if not camera.initialize_camera():
        logger.critical("Cannot proceed without camera. Exiting.")
        sys.exit(1)
        
    # Start logging session
    session_logger.start_session()
    
    # Calibration timers
    calibration_start_time = time.time()
    classifier.start_calibration()
    
    # FPS computation variables
    prev_time = time.time()
    fps = config.TARGET_FPS
    
    # Screenshot state tracking
    last_screenshot_state = "Awake"
    
    logger.info("Entering main application loop.")
    logger.info("Press 'q' to Quit, 'c' to Re-Calibrate threshold.")
    
    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret or frame is None:
                logger.error("Empty frame received. Skipping frame.")
                time.sleep(0.01)
                continue
                
            # Flip frame horizontally for natural mirror effect
            frame = cv2.flip(frame, 1)
            img_h, img_w, _ = frame.shape
            
            # FPS calculation
            curr_time = time.time()
            time_diff = curr_time - prev_time
            if time_diff > 0:
                # 0.9 smoothing factor for FPS displaying stability
                fps = 0.9 * fps + 0.1 * (1.0 / time_diff)
            prev_time = curr_time
            
            # 1. Face detection
            landmarks = detector.detect_landmarks(frame)
            
            state = "Awake"
            ear = 0.0
            eye_pts = {}
            
            if landmarks is not None:
                # Extract eye landmarks and convert to pixel coordinates
                eye_pts = detector.get_eye_landmarks(landmarks, img_w, img_h)
                
                # Calculate current average EAR
                ear = analyzer.calculate_average_ear(eye_pts["left"], eye_pts["right"])
                
                # Check Calibration Status
                if not classifier.is_calibrated:
                    elapsed_cal = time.time() - calibration_start_time
                    calibration_progress = min((elapsed_cal / config.CALIBRATION_DURATION) * 100, 100)
                    
                    classifier.collect_calibration_ear(ear)
                    state, smoothed_ear = classifier.update(ear) # updates history, returns 'Calibrating'
                    
                    if elapsed_cal >= config.CALIBRATION_DURATION:
                        classifier.finalize_calibration(
                            threshold_ratio=config.CALIBRATION_THRESHOLD_RATIO,
                            min_threshold=config.MIN_EAR_THRESHOLD
                        )
                        logger.info("Calibration phase finalized successfully.")
                else:
                    # Regular Operation
                    state, smoothed_ear = classifier.update(ear)
                    alert_manager.process_state(state)
                    session_logger.log_state_transition(state, ear)
                    session_logger.record_ear(ear)
                    
                # Draw eye landmarks and overlay contours
                frame = renderer.draw_eye_contours(frame, eye_pts, state)
            else:
                # No face detected: Handle detection loss to prevent false alarms
                if classifier.is_calibrated:
                    state = "Awake" # Reset state to avoid alert stuck in looping play
                    classifier.reset()
                    alert_manager.process_state(state)
                    session_logger.log_state_transition(state, 0.0)
                else:
                    state = "Calibrating"
                    # Reset calibration start time so user has a fresh start when they return
                    calibration_start_time = time.time()
                    classifier.start_calibration()
                
                # Display Face Not Detected warning
                cv2.putText(frame, "FACE NOT DETECTED", (20, 120), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            
            # 2. Rendering UI Overlays
            cal_prog = calibration_progress if not classifier.is_calibrated else 0.0
            frame = renderer.draw_status(
                frame=frame,
                state=state,
                ear=ear,
                threshold=classifier.threshold,
                fps=fps,
                calibration_progress=cal_prog
            )
            
            # 3. Blinking / Warning borders
            frame = renderer.draw_alert_border(frame, state)
            
            # 4. Save screenshot on state transition (Drowsy / Sleeping)
            if state != last_screenshot_state:
                if state in ["Drowsy", "Sleeping"]:
                    screenshot_path = os.path.join(config.LOG_DIR, f"{state.lower()}_capture.jpg")
                    try:
                        cv2.imwrite(screenshot_path, frame)
                        logger.info(f"Captured state screenshot: {screenshot_path}")
                    except Exception as e:
                        logger.error(f"Failed to save screenshot: {e}")
                last_screenshot_state = state
            
            # Show the output frame
            cv2.imshow("SmartEye - Realtime Monitor", frame)
            
            # Key event handling
            key = cv2.waitKey(1)
            if key != -1:
                key_masked = key & 0xFF
                try:
                    key_char = chr(key)
                except ValueError:
                    key_char = ""
                
                logger.info(f"Key pressed: raw={key}, masked={key_masked}, char={repr(key_char)}")
                    
                if key_masked == ord('q') or key_masked == ord('Q') or key_char in ['q', 'Q', 'ㅂ', 'ㅃ']:
                    logger.info("Quit key pressed.")
                    break
                elif key_masked == ord('c') or key_char in ['c', 'C', 'ㅊ']:
                    logger.info("Manual calibration trigger key pressed.")
                    classifier.start_calibration()
                    calibration_start_time = time.time()
                
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        alert_manager.cleanup()
        detector.close()
        camera.release()
        cv2.destroyAllWindows()
        logger.info("SmartEye terminated cleanly.")

if __name__ == "__main__":
    main()

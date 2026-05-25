import os
import time
import csv
import logging

logger = logging.getLogger("SmartEye.SessionLogger")

class SessionLogger:
    """Logs session state transitions and durations to a CSV file for analytics."""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.log_file_path = None
        self.current_state = "Awake"
        self.state_start_time = time.time()
        self.ear_values_in_state = []
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

    def start_session(self):
        """Creates a new CSV log file for the active session."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(self.log_dir, f"session_{timestamp}.csv")
        self.state_start_time = time.time()
        self.current_state = "Awake"
        self.ear_values_in_state = []
        
        try:
            with open(self.log_file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Elapsed_Seconds", "From_State", "To_State", "Duration_Seconds", "Average_EAR"])
            logger.info(f"Log session started. Writing to: {self.log_file_path}")
        except Exception as e:
            logger.error(f"Failed to create session log file: {e}")

    def log_state_transition(self, new_state: str, current_ear: float):
        """Records a state change event and logs metrics of the previous state."""
        self.ear_values_in_state.append(current_ear)
        
        if new_state == self.current_state:
            return
            
        now = time.time()
        duration = now - self.state_start_time
        avg_ear = sum(self.ear_values_in_state) / len(self.ear_values_in_state) if self.ear_values_in_state else 0.0
        
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_since_start = now - self.state_start_time  # Simple elapsed
        
        if self.log_file_path:
            try:
                with open(self.log_file_path, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp_str,
                        f"{now:.2f}",
                        self.current_state,
                        new_state,
                        f"{duration:.2f}",
                        f"{avg_ear:.4f}"
                    ])
            except Exception as e:
                logger.error(f"Failed to append transition to log: {e}")
                
        logger.info(f"Session transition recorded: {self.current_state} -> {new_state} (Duration: {duration:.2f}s, Avg EAR: {avg_ear:.3f})")
        
        # Reset state parameters
        self.current_state = new_state
        self.state_start_time = now
        self.ear_values_in_state = [current_ear]

    def record_ear(self, ear: float):
        """Stores the current frame's EAR value for calculating state averages."""
        self.ear_values_in_state.append(ear)

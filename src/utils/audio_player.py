import subprocess
import threading
import sys
import os
import time
import logging

logger = logging.getLogger("SmartEye.AudioPlayer")

class AudioPlayer:
    """Asynchronously plays warning sounds using native OS commands or terminal beeps."""
    
    def __init__(self):
        self.process = None
        self.is_playing = False
        self.play_thread = None
        self.sound_path = None

    def start_alert(self, sound_path: str = None):
        """Starts looping the alert sound in a separate thread if not already playing."""
        if self.is_playing:
            return
            
        self.sound_path = sound_path
        self.is_playing = True
        self.play_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.play_thread.start()
        logger.info("Alert audio started.")

    def stop_alert(self):
        """Stops playing the alert sound and terminates the playback process."""
        if not self.is_playing:
            return
            
        self.is_playing = False
        if self.process:
            try:
                self.process.terminate()
            except Exception as e:
                logger.debug(f"Error terminating audio process: {e}")
            self.process = None
            
        logger.info("Alert audio stopped.")

    def _run_loop(self):
        """Internal playback loop run in a background thread."""
        while self.is_playing:
            if sys.platform == "darwin":  # macOS
                if self.sound_path and os.path.exists(self.sound_path):
                    cmd = ["afplay", self.sound_path]
                else:
                    # Native macOS alert sound fallback
                    cmd = ["afplay", "/System/Library/Sounds/Tink.aiff"]
                
                try:
                    self.process = subprocess.Popen(cmd)
                    self.process.wait()
                except Exception as e:
                    logger.error(f"afplay audio playback failed: {e}")
                    time.sleep(1.0)
            elif sys.platform == "win32":  # Windows
                try:
                    import winsound
                    if self.sound_path and os.path.exists(self.sound_path):
                        winsound.PlaySound(self.sound_path, winsound.SND_FILENAME)
                    else:
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                except Exception as e:
                    logger.error(f"Windows audio playback failed: {e}")
                    print("\a", end="", flush=True)
                    time.sleep(0.8)
            else:
                # Linux fallback - print ascii bell and sleep
                print("\a", end="", flush=True)
                time.sleep(0.8)
                
            time.sleep(0.1)  # Brief pause between loops

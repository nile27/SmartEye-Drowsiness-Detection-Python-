import logging
from src.utils.audio_player import AudioPlayer

logger = logging.getLogger("SmartEye.AlertManager")

class AlertManager:
    """Manages audio alerts and visual flash triggers based on the classified drowsiness state."""
    
    def __init__(self, alert_sound_path: str = None):
        self.alert_sound_path = alert_sound_path
        self.audio_player = AudioPlayer()
        self.current_state = "Awake"
        self.visual_flash_active = False

    def process_state(self, state: str):
        """Processes the state and triggers appropriate audio/visual alerts.
        
        Args:
            state: The current state ('Awake', 'Drowsy', 'Sleeping', 'Calibrating')
        """
        if state == self.current_state:
            return
            
        logger.info(f"AlertManager state transition: {self.current_state} -> {state}")
        self.current_state = state
        
        if state == "Sleeping":
            self.visual_flash_active = True
            # Play loud warning sound
            self.audio_player.start_alert(self.alert_sound_path)
        elif state == "Drowsy":
            self.visual_flash_active = False
            # Play moderate alert sound
            self.audio_player.start_alert()  # Plays default fallback sound
        else:
            # Awake or Calibrating
            self.visual_flash_active = False
            self.audio_player.stop_alert()

    def cleanup(self):
        """Cleans up resources and stops audio."""
        self.audio_player.stop_alert()

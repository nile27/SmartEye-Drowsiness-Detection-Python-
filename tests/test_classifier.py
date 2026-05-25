import unittest
from unittest.mock import patch
from src.classifier import DrowsinessClassifier

class TestDrowsinessClassifier(unittest.TestCase):
    def setUp(self):
        # Initialize classifier with: threshold=0.2, drowsy=1.0s, sleeping=3.0s, smoothing=3 frames
        self.classifier = DrowsinessClassifier(
            initial_threshold=0.2,
            drowsy_time_threshold=1.0,
            sleeping_time_threshold=3.0,
            smoothing_window=3
        )

    def test_smoothing(self):
        # Complete calibration so update runs classification
        self.classifier.is_calibrated = True
        
        # Buffer window is 3. Send 0.3, 0.3, 0.3. Smoothed EAR should be 0.3.
        state, smoothed = self.classifier.update(0.3)
        self.assertAlmostEqual(smoothed, 0.3)
        self.assertEqual(state, "Awake")

        # Send 0.3, 0.1, 0.1. Smoothed EAR should be (0.3+0.1+0.1)/3 = 0.1667 (< 0.2 threshold)
        self.classifier.update(0.1)
        state, smoothed = self.classifier.update(0.1)
        self.assertAlmostEqual(smoothed, 0.16666666666666666)

    def test_calibration(self):
        self.classifier.start_calibration()
        self.assertFalse(self.classifier.is_calibrated)
        
        # Collect some values (average = 0.3)
        self.classifier.collect_calibration_ear(0.3)
        self.classifier.collect_calibration_ear(0.3)
        self.classifier.collect_calibration_ear(0.3)
        
        # Finalize calibration with ratio 0.7
        self.classifier.finalize_calibration(threshold_ratio=0.7)
        self.assertTrue(self.classifier.is_calibrated)
        self.assertAlmostEqual(self.classifier.threshold, 0.21)

    @patch('time.time')
    def test_state_transitions(self, mock_time):
        self.classifier.is_calibrated = True
        
        # Set start time to 100.0
        mock_time.return_value = 100.0
        
        # 1. EAR is high -> State is Awake
        state, _ = self.classifier.update(0.3)
        self.assertEqual(state, "Awake")
        
        # 2. EAR drops below threshold (0.2)
        # First frame: timer starts, but elapsed time is 0.0s -> Awake
        state, _ = self.classifier.update(0.1)
        self.assertEqual(state, "Awake")
        
        # 3. Simulate elapsed time = 0.5s (under drowsy threshold 1.0s) -> Awake
        mock_time.return_value = 100.5
        state, _ = self.classifier.update(0.1)
        self.assertEqual(state, "Awake")
        
        # 4. Simulate elapsed time = 1.2s (above drowsy threshold 1.0s, from 100.5 start time) -> Drowsy
        mock_time.return_value = 101.7
        state, _ = self.classifier.update(0.1)
        self.assertEqual(state, "Drowsy")
        
        # 5. Simulate elapsed time = 3.6s (above sleeping threshold 3.0s, from 100.5 start time) -> Sleeping
        mock_time.return_value = 104.1
        state, _ = self.classifier.update(0.1)
        self.assertEqual(state, "Sleeping")
        
        # 6. EAR goes back above threshold -> Resets to Awake
        state, _ = self.classifier.update(0.4)
        self.assertEqual(state, "Awake")
        self.assertIsNone(self.classifier.closed_start_time)

if __name__ == "__main__":
    unittest.main()

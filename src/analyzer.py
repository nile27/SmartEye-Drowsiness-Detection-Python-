import math
# pyrefly: ignore [missing-import]
import numpy as np
import logging

logger = logging.getLogger("SmartEye.EyeAnalyzer")

class EyeAnalyzer:
    """Computes the Eye Aspect Ratio (EAR) from eye landmark points."""
    
    @staticmethod
    def calculate_distance(p1: tuple[int, int], p2: tuple[int, int]) -> float:
        """Calculates Euclidean distance between two 2D points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def calculate_ear(self, eye_pts: list[tuple[int, int]]) -> float:
        """Calculates the Eye Aspect Ratio (EAR) for a single eye.
        
        Indices mapping in eye_pts:
            p1: [0] (inner corner)
            p2: [1] (top-inner)
            p3: [2] (top-outer)
            p4: [3] (outer corner)
            p5: [4] (bottom-outer)
            p6: [5] (bottom-inner)
            
        Formula: EAR = (|p2 - p6| + |p3 - p5|) / (2.0 * |p1 - p4|)
        """
        if len(eye_pts) < 6:
            return 0.0
            
        # Vertical distances
        v1 = self.calculate_distance(eye_pts[1], eye_pts[5]) # p2 - p6
        v2 = self.calculate_distance(eye_pts[2], eye_pts[4]) # p3 - p5
        
        # Horizontal distance
        h = self.calculate_distance(eye_pts[0], eye_pts[3]) # p1 - p4
        
        if h == 0.0:
            return 0.0
            
        ear = (v1 + v2) / (2.0 * h)
        return ear

    def calculate_average_ear(self, left_eye_pts: list[tuple[int, int]], right_eye_pts: list[tuple[int, int]]) -> float:
        """Calculates the average EAR for both eyes."""
        left_ear = self.calculate_ear(left_eye_pts)
        right_ear = self.calculate_ear(right_eye_pts)
        return (left_ear + right_ear) / 2.0

import unittest
from src.analyzer import EyeAnalyzer

class TestEyeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = EyeAnalyzer()

    def test_calculate_distance(self):
        # 3-4-5 triangle test
        p1 = (0, 0)
        p2 = (3, 4)
        dist = self.analyzer.calculate_distance(p1, p2)
        self.assertAlmostEqual(dist, 5.0)

    def test_calculate_ear_standard(self):
        # Setup mock eye points for EAR = 0.4
        # p1: (0,0), p2: (3,2), p3: (7,2), p4: (10,0), p5: (7,-2), p6: (3,-2)
        # v1 (p2 to p6) = y-diff 4, x-diff 0 = 4.0
        # v2 (p3 to p5) = y-diff 4, x-diff 0 = 4.0
        # h (p1 to p4) = y-diff 0, x-diff 10 = 10.0
        # EAR = (4.0 + 4.0) / (2.0 * 10.0) = 8.0 / 20.0 = 0.4
        eye_pts = [
            (0, 0),   # p1 (inner corner)
            (3, 2),   # p2 (top-inner)
            (7, 2),   # p3 (top-outer)
            (10, 0),  # p4 (outer corner)
            (7, -2),  # p5 (bottom-outer)
            (3, -2)   # p6 (bottom-inner)
        ]
        ear = self.analyzer.calculate_ear(eye_pts)
        self.assertAlmostEqual(ear, 0.4)

    def test_calculate_ear_zero_horizontal(self):
        # Eye points where outer/inner corner are same (division by zero test)
        eye_pts = [
            (0, 0),
            (0, 2),
            (0, 2),
            (0, 0),
            (0, -2),
            (0, -2)
        ]
        ear = self.analyzer.calculate_ear(eye_pts)
        self.assertEqual(ear, 0.0)

    def test_calculate_ear_insufficient_points(self):
        eye_pts = [(0, 0), (1, 1)]
        ear = self.analyzer.calculate_ear(eye_pts)
        self.assertEqual(ear, 0.0)

if __name__ == "__main__":
    unittest.main()

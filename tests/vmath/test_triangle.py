import unittest
import math
from brlcad.vmath import Vector, Triangle


class TriangleTestCase(unittest.TestCase):

    angle_checks = (
        ("1, 1, 1", "-1, -1, -1", "0.5, 0.5, 0.5", math.pi),
        ("1, 1, 1", "1, 1, 1", "2,2,2", 0),
        ("1, 0.5, 0.5", "-1, 1, 1", "0, 1.5, 1.5", math.pi/2),
    )

    def test_angle_between_vectors(self):
        for x in self.angle_checks:
            angle = Triangle.angle_between_vectors(x[0], x[1])
            self.assertAlmostEqual(
                x[3], angle, places=10,
                msg="Check failed for: {}; result is: {}".format(x, angle)
            )

    def test_angle_from_points(self):
        for x in self.angle_checks:
            angle = Triangle.angle_from_points(x[0], x[2], x[1])
            self.assertAlmostEqual(
                x[3], angle, places=10,
                msg="Check failed for: {}; result is: {}".format(x, angle)
            )

if __name__ == "__main__":
    unittest.main()

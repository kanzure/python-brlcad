"""
Math for calculating components of a triangle.
"""
import math
from brlcad.vmath import Vector


# TODO: implement the object - this is currently just a stub where convenience methods live
class Triangle(object):
    """
    Represents a triangle constructed from different other geometrical entities.
    """

    # Utility methods for calculating triangle related
    # geometry elements without creating a Triangle object

    @staticmethod
    def angle_between_vectors(v1, v2):
        """
        Calculates the angle between <v1> and <v2>. The result is in the range [0, pi]
        On degenerate input (any of the vectors of norm 0) will raise ValueError.
        """
        v1 = Vector(v1, copy=False)
        v2 = Vector(v2, copy=False)
        n1 = v1.norm()
        n2 = v2.norm()
        if n1 == 0 or n2 == 0:
            raise ValueError("Can't calculate angle between zero length vectors !")
        cos_a = v1.dot(v2) / (n1 * n2)
        cos_a = max(-1.0, min(1.0, cos_a))
        return math.acos(cos_a)

    @staticmethod
    def angle_from_points(p1, p2, p3):
        """
        Calculates the angle p1-p2-p3. The result is in the range [0, pi]
        """
        p1 = Vector(p1, copy=False)
        p2 = Vector(p2, copy=False)
        p3 = Vector(p3, copy=False)
        return Triangle.angle_between_vectors(p1 - p2, p3 - p2)

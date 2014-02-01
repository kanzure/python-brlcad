"""
Maths related to plane geometry.
"""
from vector import Vector
import numpy as np

class Plane(object):
    """
    A plane represented by a normal vector perpendicular to the
    plane and the shortest distance from the origin to the plane.
    Having a negative distance makes sense and means the plane is
    pointing to the Origin, positive distances mean pointing outwards.
    """

    def __init__(self, normal, distance, copy=False):
        self.normal = Vector(normal, copy=copy).assure_normal()
        self.distance = distance

    def is_same(self, other, rtol=1.e-5, atol=1.e-8):
        normal_same = self.normal.is_same(other.normal, rtol=rtol, atol=atol)
        distance_same = np.allclose(self.distance, other.distance, rtol=rtol, atol=atol)
        return normal_same and distance_same

    @staticmethod
    def from_point_and_normal(p, n, copy=False):
        """
        Creates a Plane object from a point p on the plane and a vector n perpendicular to the plane.
        """
        normal = Vector(n, copy=copy).assure_normal()
        return Plane(normal, normal.dot(Vector(p, copy=False)))

    def __iter__(self):
        for x in self.normal:
            yield x
        yield self.distance

    def __repr__(self):
        return "Plane({0}, {1})".format(self.normal, self.distance)

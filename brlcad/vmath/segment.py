"""
Segment-based geometry.
"""
import math
from plane import Plane
from vector import Vector
import numpy as np


class Segment(object):
    """
    A segment described by 2 vectors: the starting point and the direction/length vector.
    """

    def __init__(self, point, direction):
        self.start = Vector(point, copy=False)
        self.direction = Vector(direction, copy=False)

    def rotate_point(self, point, angle):
        """
        Rotates the point around this segment with <angle> radians.
        Returns the resulting new point.
        Examples:
        >>> x = Segment("1,1,1", "1,1,1")
        >>> x.rotate_point("2, 2, 2", 10).is_same([2, 2, 2])
        True
        >>> x.rotate_point([1, 0, 0], 2 * math.pi/3).is_same([0, 1, 0])
        True
        >>> x.rotate_point([1, 0, 0], -2 * math.pi/3).is_same([0, 0, 1])
        True
        >>> y = Segment([0, 0, 0], [0, 1, 0])
        >>> y.rotate_point([1, 0, 0], math.pi / 2).is_same([0, 0, -1])
        True
        >>> y.rotate_point([1, 0, 0], -math.pi / 2).is_same([0, 0, 1])
        True
        """
        normal = self.direction.assure_normal()
        if normal.is_same((0, 0, 0)):
            raise ValueError("Can't rotate around a 0 length segment")
        point = Vector(point, copy=False)
        sina = math.sin(angle)
        cosa = math.cos(angle)
        if np.allclose(sina, 0) and np.allclose(cosa, 1):
            # this is a shortcut worth making, to get the exact same point for angles 2n*PI
            return point
        ap = point - self.start
        x = normal.cross(ap)
        cosdot = ap.dot(normal) * (1 - cosa)

        return self.start + (cosa * ap) + (cosdot * normal) + (sina * x)

    def normalize(self):
        """
        Normalizes the direction vector, resulting in a norm 1 segment with the same start point.
        """
        self.direction.normalize()
        return self

    def normal_plane(self):
        """
        Returns the Plane which contains the start point and it is normal to the direction.
        >>> x = Segment("1,1,1", "1,1,1")
        >>> n = math.sqrt(3)
        >>> x.normal_plane().is_same(Plane([1/n, 1/n, 1/n], n))
        True
        >>> y = Segment([0, 0, 0], [0, 1, 0])
        >>> y.normal_plane().is_same(Plane("0, 1, 0", 0))
        True
        """
        normal = self.direction.assure_normal()
        if normal.is_same((0, 0, 0)):
            raise ValueError("Can't have a normal plane for a 0 length segment")
        return Plane(normal.copy(), normal.dot(self.start))

    def is_same(self, other, rtol=1.e-5, atol=1.e-8):
        start_same = self.start.is_same(other.start, rtol=rtol, atol=atol)
        dir_same = self.direction.is_same(other.direction, rtol=rtol, atol=atol)
        return start_same and dir_same

    def __repr__(self):
        return "Segment({0}, {1})".format(self.start, self.direction)

    def __iter__(self):
        for x in self.start:
            yield x
        for x in self.direction:
            yield x

if __name__ == "__main__":
    import doctest
    np.set_printoptions(suppress=True, precision=5)
    doctest.testmod()

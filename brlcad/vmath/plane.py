"""
Maths related to plane geometry.
"""
import collections
from vector import Vector
import numpy as np


class Plane(object):
    """
    A plane represented by a normal vector N perpendicular to the
    plane and the shortest distance d from the origin to the plane.

    The plane is defined as the points P which satisfy the condition
    that the projection of OP on the line defined by N is of length d:

    N.dot(P) = d

    Having a negative distance makes sense and means the plane normal is
    pointing from the plane to the Origin (the half-space defined by
    the plane will not contain the origin), positive distances mean
    the half-space defined will contain the origin, and the plane
    normal points from the origin to the plane.

    In the following figure the plane normal N (=PN) is the same for both
    planes, but the distance d (=OP) is positive for plane_1 and negative
    for plane_2.

    The half-space defined by the planes is below the planes
    (opposite direction to where the plane normal is pointing), for
    both plane_1 and plane_2, because of the plane normal being the same.
    The half-space for plane_1 contains the origin, the one for
    plane_2 does not.

    The condition of a point P to be contained by the half-space is:

    N.dot(P) <= d

                   z
                   |
                   |
             +-----|-----------plane_1--+
            /      *                   /
         +  ;      '                   ;
        N \/       '                  / Half space
           \       '                  ; contains the origin
          / \ d(>0)'                 /
          ;  *     '                 ;
         /  P .    '                /
         +-------------------------+
                \  |
                 \ |
                  \|
                 O +------y
                  / \
             +---/---\-N-------plane_2--+
            /   /     +                /
            ;   x      \               ;
           /            \ d(<0)       / Half space does not
           ;             *            ; contain the origin
          /             P            /
          ;                          ;
         /                          /
         +-------------------------+

    Notation:
        d = OP -> distance from the origin to the plane
        N = PN -> unit vector normal to the plane, giving it's orientation

    """
    def __init__(self, normal, distance, copy=False):
        normal = Vector(normal, copy=copy)
        self.normal = normal.assure_normal(error_message="Can't define a plane with 0 length normal !")
        self.distance = float(distance)

    def is_same(self, other, rtol=1.e-5, atol=1.e-8):
        normal_same = self.normal.is_same(other.normal, rtol=rtol, atol=atol)
        distance_same = np.allclose(self.distance, other.distance, rtol=rtol, atol=atol)
        return normal_same and distance_same

    def copy(self):
        return Plane(self.normal, self.distance, copy=True)

    @staticmethod
    def from_point_and_normal(p, n, copy=False):
        """
        Creates a Plane object from a point p on the plane and a vector n perpendicular to the plane.
        """
        normal = Vector(n, copy=copy)
        return Plane(normal, normal.dot(Vector(p, copy=False)))

    @staticmethod
    def wrap(values, copy=False):
        """
        Parses a Plane object from mostly everything which provides 4 floats, including a string:
        >>> Plane.wrap("1,0,0,4")
        Plane(Vector([ 1.,  0.,  0.]), 4.0)
        >>> Plane.wrap((0, -1, 0, 2))
        Plane(Vector([ 0., -1.,  0.]), 2.0)
        >>> x = Plane.wrap([0, 0, 10, 3])
        >>> x
        Plane(Vector([ 0.,  0.,  1.]), 3.0)
        >>> x is Plane.wrap(x)
        True
        >>> y = Plane.wrap(x, copy=True)
        >>> x is y
        False
        >>> x.is_same(y)
        True
        """
        if isinstance(values, Plane):
            return values.copy() if copy else values
        is_string = isinstance(values, str)
        is_iterable = isinstance(values, collections.Iterable)
        is_sized = isinstance(values, collections.Sized)
        if is_string or not is_iterable or not is_sized:
            values = Vector(values)
        elif len(values) == 2:
            return Plane(normal=values[0], distance=values[1], copy=copy)
        if len(values) == 4:
            return Plane(normal=values[:3], distance=values[3], copy=copy)
        raise ValueError("Can't parse a plane from: {0}".format(values))

    def __iter__(self):
        for x in self.normal:
            yield x
        yield self.distance

    def __repr__(self):
        return "Plane({0}, {1})".format(repr(self.normal), self.distance)

    def contains(self, point):
        """
        True if this plane contains the given point, False otherwise.
        """
        point = Vector(point, copy=False)
        return np.allclose(self.normal.dot(point), self.distance)

    def compare_for_sort(self, other):
        result = self.distance - other.distance
        if result:
            return result
        return self.normal.compare_for_sort(other.normal)

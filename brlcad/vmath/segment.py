"""
Segment-based geometry.
"""
import math
from brlcad.vmath.geometry_object import GeometryObject, create_property
from plane import Plane
from vector import Vector
import numpy as np


class Segment(GeometryObject):
    """
    A segment described by 2 vectors: the <start_point> and <delta>.
    """

    # Structures to be override from super-class:

    calc_function_map = dict()

    param_wrappers = dict()

    canonical_init_params = {
        "start_point", "delta"
    }

    # end of structures to be overridden

    def __init__(self, verify=False, **kwargs):
        """
        Create a segment based on one of the possible parameter sets.
        The following combinations are accepted:
        * (start_point, end_point)
        * (start_point, delta)
        * (start_point, delta_unit, length)
        If more parameters are already available, and checking is required,
        use verify=True (default is False, meaning parameters are not checked for consistency).
        Parameters which are not set will be calculated if needed, but at least one of
        the above mentioned combinations must be provided completely.
        """
        GeometryObject.__init__(self, verify=verify, **kwargs)

    def is_same(self, other, rtol=1.e-5, atol=1.e-8):
        start_same = self.start_point.is_same(other.start_point, rtol=rtol, atol=atol)
        delta_same = self.delta.is_same(other.delta, rtol=rtol, atol=atol)
        return start_same and delta_same

    def __iter__(self):
        for x in self.start_point:
            yield x
        for x in self.delta:
            yield x

    # Property declarations/calculation functions

    start_point = create_property(
        name="start_point",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="Start point of the segment"
    )

    def _calculate_delta(self):
        start_point = self.start_point
        if start_point is None:
            return None
        if self.is_set("end_point"):
            end_point = self.end_point
            if end_point is not None:
                return end_point - start_point
        delta_unit = self.delta_unit
        length = self.length
        if delta_unit is not None and length is not None:
            return delta_unit * length
        return None

    delta = create_property(
        name="delta",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The vector pointing from <start_point> to <end_point>."
    )

    def _calculate_mid_point(self):
        start_point = self.start_point
        if start_point is None:
            return None
        if self.is_set("end_point"):
            end_point = self.end_point
            if end_point is not None:
                return (start_point + end_point) * 0.5
        delta = self.delta
        if delta is not None:
            return start_point + 0.5 * delta
        return None

    mid_point = create_property(
        name="mid_point",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The middle point of the segment."
    )

    def _calculate_delta_unit(self):
        delta = self.delta
        if delta is not None:
            return delta.assure_normal("0 length segment has no <delta_unit>")
        return None

    delta_unit = create_property(
        name="delta_unit",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The unit vector pointing from <start_point> towards <end_point>."
    )

    def _calculate_end_point(self):
        start_point = self.start_point
        delta = self.delta
        if start_point is not None and delta is not None:
            return start_point + delta
        return None

    end_point = create_property(
        name="end_point",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The end point of the segment."
    )

    def _calculate_length(self):
        delta = self.delta
        if delta is not None:
            return delta.norm()
        return None

    length = create_property(
        name="length",
        context=locals(),
        param_wrapper=float,
        doc="The length of the segment."
    )

    def _calculate_normal_plane(self):
        """
        The Plane which contains the <start_point> and it is normal to the <delta> vector.
        The resulting half-space will not contain the end point.
        >>> x = Segment(start_point="1,1,1", delta="1,1,1")
        >>> n = math.sqrt(3)
        >>> x.normal_plane.is_same(Plane([1/n, 1/n, 1/n], n))
        True
        >>> y = Segment(start_point=[0, 0, 0], delta=[0, 1, 0])
        >>> y.normal_plane.is_same(Plane("0, 1, 0", 0))
        True
        """
        normal = self.delta_unit
        return Plane(normal, normal.dot(self.start_point))

    normal_plane = create_property(
        name="normal_plane",
        context=locals(),
        param_wrapper=Plane.wrap,
    )

    # Utility methods for calculating segment related geometry

    def rotate_point(self, point, angle):
        """
        Rotates the point around this segment with <angle> radians.
        Returns the resulting new point.
        Examples:
        >>> x = Segment(start_point="1,1,1", delta="1,1,1")
        >>> x.rotate_point("2, 2, 2", 10).is_same([2, 2, 2])
        True
        >>> x.rotate_point([1, 0, 0], 2 * math.pi/3).is_same([0, 1, 0])
        True
        >>> x.rotate_point([1, 0, 0], -2 * math.pi/3).is_same([0, 0, 1])
        True
        >>> y = Segment(start_point=[0, 0, 0], delta=[0, 1, 0])
        >>> y.rotate_point([1, 0, 0], math.pi / 2).is_same([0, 0, -1])
        True
        >>> y.rotate_point([1, 0, 0], -math.pi / 2).is_same([0, 0, 1])
        True
        """
        normal = self.delta_unit
        point = Vector(point, copy=False)
        sin_angle = math.sin(angle)
        cos_angle = math.cos(angle)
        if np.allclose(sin_angle, 0) and np.allclose(cos_angle, 1):
            # this is a shortcut worth making, to get the exact same point for angles 2n*PI
            return point
        ap = point - self.start_point
        x = normal.cross(ap)
        cos_dot = ap.dot(normal) * (1 - cos_angle)

        return self.start_point + (cos_angle * ap) + (cos_dot * normal) + (sin_angle * x)


if __name__ == "__main__":
    import doctest
    np.set_printoptions(suppress=True, precision=5)
    doctest.testmod()

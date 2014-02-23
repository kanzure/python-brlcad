"""
Python wrapper for the Pipe primitive of BRL-CAD.
"""
import collections
import functools
from base import Primitive
from brlcad.vmath import Vector
import ctypes
import brlcad._bindings.librt as librt


def getter(index, obj):
    return obj.items[index]


def setter(index, obj, value):
    obj.items[index] = value


class PipePoint(collections.Sequence):

    def __new__(cls, point, d_outer=0.5, d_inner=0.3, r_bend=1, copy=False):
        """
        Parse a PipePoint from multiple possible inputs:
        >>> x = PipePoint("0, 1, 2", 3, 2, 5)
        >>> x.point.is_same((0, 1, 2))
        True
        >>> (x.d_outer, x.d_inner, x.r_bend) == (3, 2, 5)
        True
        >>> x[0] is x.point
        True
        >>> [x.d_outer, x.d_inner, x.r_bend] == x[1:]
        True
        >>> x is PipePoint(x)
        True
        >>> y = PipePoint(x, copy=True)
        >>> x is y
        False
        >>> x.is_same(y)
        True
        >>> x.is_same(PipePoint((0, 1, 2), 3, 2, 5))
        True
        >>> x.is_same(PipePoint(point=(0, 1, 2), d_inner=2, d_outer=3, r_bend=5))
        True
        >>> x.is_same(PipePoint([(0, 1, 2), 3, 2, 5]))
        True
        >>> x.is_same(PipePoint(("0, 1, 2", 3, 2, 5)))
        True
        """
        if isinstance(point, PipePoint):
            if copy:
                return PipePoint(*point, copy=True)
            else:
                return point
        result = collections.Sequence.__new__(cls)
        is_non_string_sequence = isinstance(point, collections.Sequence) and not isinstance(point, str)
        if is_non_string_sequence and len(point) == 4:
            # this means the parameters were wrapped in a sequence, so we unwrap them
            point, d_outer, d_inner, r_bend = point
        result.items = [Vector(point, copy=copy), float(d_outer), float(d_inner), float(r_bend)]
        return result

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "{}(point={}, d_outer={}, d_inner={}, r_bend={})".format(
            self.__class__.__name__, repr(self.point), self.d_outer, self.d_inner, self.r_bend
        )

    point = property(fget=functools.partial(getter, 0), fset=functools.partial(setter, 0))
    d_outer = property(fget=functools.partial(getter, 1), fset=functools.partial(setter, 1))
    d_inner = property(fget=functools.partial(getter, 2), fset=functools.partial(setter, 2))
    r_bend = property(fget=functools.partial(getter, 3), fset=functools.partial(setter, 3))

    def is_same(self, other):
        other = PipePoint(other)
        return self.point.is_same(other.point) and self[1:] == other[1:]

    def is_same_point(self, other):
        other = PipePoint(other)
        return self.point.is_same(other.point)


class Pipe(Primitive):

    def __init__(self, name, points=(((0, 0, 0), 0.5, 0.3, 1), ((0, 0, 1), 0.5, 0.3, 1)), copy=False):
        Primitive.__init__(self, name=name)
        if isinstance(points, list) and not copy:
            for i in xrange(0, len(points)):
                points[i] = PipePoint(points[i])
        else:
            points = [PipePoint(point, copy=copy) for point in points]
        self.points = points

    def __repr__(self):
        return "{}({}, points={})".format(self.__class__.__name__, self.name, repr(self.points))

    def update_params(self, params):
        params.update({
            "points": self.points,
        })

    def copy(self):
        return Pipe(self.name, self.points, copy=True)

    def has_same_data(self, other):
        return all(map(PipePoint.is_same, self.points, other.points))

    def append_point(self, point, *args, **kwargs):
        """
        Adds a point to the end of the pipe. It accepts the same parameters as the PipePoint constructor.
        """
        self.points.append(PipePoint(point, *args, **kwargs))

    @staticmethod
    def from_wdb(name, data):
        points = []
        crt_head = data.pipe_segs_head.forw
        for i in xrange(0, data.pipe_count):
            crt_point = ctypes.cast(crt_head, ctypes.POINTER(librt.wdb_pipept)).contents
            crt_head = crt_point.l.forw
            points.append((
                crt_point.pp_coord, crt_point.pp_od, crt_point.pp_id, crt_point.pp_bendradius
            ))
        return Pipe(
            name=name,
            points=points,
            copy=False,
        )

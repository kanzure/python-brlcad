"""
Python wrapper for the Metaball primitive of BRL-CAD.
"""
import collections
import functools
import types
from base import Primitive
from brlcad.vmath import Vector
import ctypes
import brlcad._bindings.librt as librt
import brlcad._bindings.libbu as libbu
import brlcad.ctypes_adaptors as cta


def getter(index, obj):
    return obj.items[index]


def setter(index, obj, value):
    obj.items[index] = value


class MetaballCtrlPoint(collections.Sequence):

    def __new__(cls, point=(0, 0, 1), field_strength=1, sweat=0, copy=False):
        """
        Parse a MetaballCtrlPoint from multiple possible inputs:
        >>> x = MetaballCtrlPoint("0, 0, 1", 1, 0)
        >>> x.point.is_same((0, 0, 1))
        True
        >>> (x.field_strength, x.sweat) == (1, 0)
        True
        >>> x[0] is x.point
        True
        >>> [x.field_strength, x.sweat] == x[1:]
        True
        >>> x is MetaballCtrlPoint(x)
        True
        >>> y = MetaballCtrlPoint(x, copy=True)
        >>> x is y
        False
        >>> x.is_same(y)
        True
        >>> x.is_same(MetaballCtrlPoint((0, 0, 1), 1, 0))
        True
        >>> x.is_same(MetaballCtrlPoint(point=(0, 0, 1), field_strength=1, sweat=0))
        True
        >>> x.is_same(MetaballCtrlPoint([(0, 0, 1), 1, 0]))
        True
        >>> x.is_same(MetaballCtrlPoint(("0, 0, 1", 1, 0)))
        True
        """
        types.ListType,types.TupleType
        if isinstance(point, MetaballCtrlPoint):
            if copy:
                return MetaballCtrlPoint(*point, copy=True)
            else:
                return point
        result = collections.Sequence.__new__(cls)
        is_non_string_sequence = isinstance(point, collections.Sequence) and not isinstance(point, str)
        if is_non_string_sequence and len(point) == 3 and isinstance(point[0], (types.ListType, types.TupleType,
                                                                                types.StringType)):
            # this means the parameters were wrapped in a sequence, so we unwrap them
            point, field_strength, sweat = point
        result.items = [Vector(point, copy=copy), float(field_strength), float(sweat)]
        return result

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "{}(point={}, field_strength={}, sweat={})".format(
            self.__class__.__name__, repr(self.point), self.field_strength, self.sweat
        )

    point = property(fget=functools.partial(getter, 0), fset=functools.partial(setter, 0))
    field_strength = property(fget=functools.partial(getter, 1), fset=functools.partial(setter, 1))
    sweat = property(fget=functools.partial(getter, 2), fset=functools.partial(setter, 2))

    def is_same(self, other):
        other = MetaballCtrlPoint(other)
        return self.point.is_same(other.point) and self[1:] == other[1:]

    def is_same_point(self, other):
        other = MetaballCtrlPoint(other)
        return self.point.is_same(other.point)


class Metaball(Primitive):

    def __init__(self, name, threshold=1, method=2, points=(((1, 1, 1), 1, 0), ((0, 0, 1), 2, 0)), copy=False):
        Primitive.__init__(self, name=name)
        if isinstance(points, list) and not copy:
            for i in xrange(0, len(points)):
                points[i] = MetaballCtrlPoint(points[i])
        else:
            points = [MetaballCtrlPoint(point, copy=copy) for point in points]
        self.threshold = threshold if threshold > 0 else 1
        self.method = method if method > 0 else 2
        self.points = points

    def __repr__(self):
        return "{}({}, threshold={}, method={}, points={})".format(
            self.__class__.__name__,
            self.name,
            self.threshold,
            self.get_method_name(),
            repr(self.points))

    def update_params(self, params):
        params.update({
            "threshold": self.threshold,
            "method": self.method,
            "points": self.points
        })

    def copy(self):
        return Metaball(self.name, self.threshold, self.method, self.points, copy=True)

    def has_same_data(self, other):
        return all(map(MetaballCtrlPoint.is_same, self.points, other.points)) and \
                self.threshold == other.threshold and \
                self.method == other.method

    def get_method_name(self):
        if self.method == 0:
            return "METABALL"
        elif self.method == 1:
            return "ISOPOTENTIAL"
        else:
            return "BLOB"

    @staticmethod
    def from_wdb(name, data):
        points=[]
        crt_head = data.metaball_ctrl_head.forw
        while(1):
            crt_point = ctypes.cast(crt_head, ctypes.POINTER(librt.wdb_metaballpt)).contents
            crt_head = crt_point.l.forw
            points.append((
                Vector(crt_point.coord), crt_point.fldstr, crt_point.sweat
            ))
            if points.__len__() > 3:
                if Vector(points[0][0]).is_same(Vector(points[-1][0])) and \
                    points[0][1] == points[-1][1] and points[0][2] == points[-1][2]:
                    points[-2:] = []
                    break;
        return Metaball(
            name=name,
            threshold=data.threshold,
            method=data.method,
            points=points,
            copy=False,
        )
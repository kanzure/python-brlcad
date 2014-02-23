"""
Python wrapper for the Sketch primitive of BRL-CAD.
"""
import collections
import numbers

from base import Primitive
from brlcad.vmath import Vector
import brlcad._bindings.librt as librt
import brlcad.ctypes_adaptors as cta
import numpy as np


def indexed_getter(index):
    return lambda obj: obj[index]


def indexed_setter(index):
    def _setter(obj, value):
        obj[index] = value
    return _setter


class Curve(collections.MutableSequence):
    """
    Represents one curve segment of a sketch. Curve instances implement the collections.MutableSequence
    interface over the points which comprise the curve, and it is possible to list/add/remove/modify the
    control points by directly using the Curve object as a list.
    For setting point values both indexes into the vertices list of the sketch as well as 2D Vectors can be used.
    The (list interface) getters will always return Vector values.
    To get the vertex index of the point, use the "vertex_index" and "vertex_index_iter" methods.
    """

    def __init__(self, sketch, points, reverse=False, copy=False):
        self.sketch = sketch
        self._points = list(points) if copy or not isinstance(points, list) else points
        for i in xrange(0, len(self._points)):
            self._points[i] = sketch.vertex_index(self._points[i])
        self.reverse = reverse

    points = property(fget=tuple, doc="Read-only view of the points in the Curve")

    def __len__(self):
        return len(self._points)

    def __delitem__(self, index):
        del self._points[index]

    def __setitem__(self, index, value):
        value = self.sketch.vertex_index(value)
        self._points[index] = value

    def __getitem__(self, index):
        return self.sketch.vertices[self._points[index]]

    def insert(self, index, value):
        return self._points.insert(index, self.sketch.vertex_index(value))

    def vertex_index(self, point_index):
        return self._points[point_index]

    def vertex_index_iter(self):
        return iter(self._points)

    def build_segment(self):
        raise NotImplementedError(
            "Curve subclass {} does not implement the build_segment method !".format(self.__class__.__name__)
        )

    def is_same(self, other):
        if bool(self.reverse) != bool(other.reverse):
            return False
        if self._points != other._points:
            return False
        if not self.is_same_data(other):
            return False
        return True

    def is_same_data(self, other):
        raise NotImplementedError(
            "Curve subclass {} does not implement the is_same_data method !".format(self.__class__.__name__)
        )


class Line(Curve):
    """
    Represents a line segment in the sketch.
    """

    def __init__(self, sketch, points, reverse=False, copy=False):
        Curve.__init__(self, sketch, points, reverse=reverse, copy=copy)

    @staticmethod
    def from_wdb(sketch, data, reverse):
        data = librt.cast(data, librt.POINTER(librt.struct_line_seg)).contents
        return Line(sketch, [data.start, data.end], reverse=reverse)

    start = property(fget=indexed_getter(0), fset=indexed_setter(0))
    end = property(fget=indexed_getter(1), fset=indexed_setter(1))

    def __repr__(self):
        return "{}(start={}, end={})".format(
            self.__class__.__name__, repr(self.start), repr(self.end)
        )

    def build_segment(self):
        result = librt.struct_line_seg()
        result.magic = librt.CURVE_LSEG_MAGIC
        result.start = self._points[0]
        result.end = self._points[1]
        return result

    def is_same_data(self, other):
        # Line data is completely covered by the Curve is_same method
        return True

    def copy_to(self, sketch):
        # todo: implement
        pass


class CircularArc(Curve):
    """
    Circular arc curve segment.
    """

    def __init__(self, sketch, points, reverse=False, radius=-1, center_is_left=False, clock_wise=False, copy=False):
        Curve.__init__(self, sketch, points, reverse=reverse, copy=copy)
        self.radius = radius
        self.center_is_left = center_is_left
        self.clock_wise = clock_wise

    @staticmethod
    def from_wdb(sketch, data, reverse):
        data = librt.cast(data, librt.POINTER(librt.struct_carc_seg)).contents
        return CircularArc(
            sketch,
            [data.start, data.end],
            reverse=reverse,
            radius=data.radius,
            center_is_left=bool(data.center_is_left),
            clock_wise=bool(data.orientation)
        )

    start = property(fget=indexed_getter(0), fset=indexed_setter(0))
    end = property(fget=indexed_getter(1), fset=indexed_setter(1))

    def __repr__(self):
        return "{}(start={}, end={}, radius={}, reverse={}, center_is_left={}, clock_wise={})".format(
            self.__class__.__name__, repr(self.start), repr(self.end),
            self.radius, self.reverse, self.center_is_left, self.clock_wise
        )

    def build_segment(self):
        result = librt.struct_carc_seg()
        result.magic = librt.CURVE_CARC_MAGIC
        result.start = self._points[0]
        result.end = self._points[1]
        result.radius = self.radius
        result.center_is_left = cta.bool(self.center_is_left)
        result.orientation = cta.bool(self.clock_wise)
        return result

    def is_same_data(self, other):
        if bool(self.center_is_left) != bool(other.center_is_left):
            return False
        if bool(self.clock_wise) != bool(other.clock_wise):
            return False
        return np.allclose(self.radius, other.radius)

    def copy_to(self, sketch):
        # todo: implement
        pass


class NURB(Curve):
    """
    NURB curve segment.
    """

    def __init__(self, sketch, points, reverse=False, point_type=None,
                 knot_vector=None, weights=None, copy=False):
        Curve.__init__(self, sketch, points, reverse=reverse, copy=copy)
        # todo: honor copy param below too:
        self.point_type = point_type
        self.knot_vector = knot_vector
        self.weights = weights

    @staticmethod
    def from_wdb(sketch, data, reverse):
        data = librt.cast(data, librt.POINTER(librt.struct_nurb_seg)).contents
        return NURB(
            sketch,
            points=[data.ctl_points[i] for i in xrange(0, data.c_size)],
            reverse=reverse,
            point_type=data.pt_type,
            knot_vector=data.k,
            weights=[data.weights[i] for i in xrange(0, data.c_size)]
        )

    degree = property(fget=lambda self: len(self.points) - 1, doc="degree of curve (number of control points - 1)")

    order = property(fget=lambda self: len(self.points) - 2, doc="order of NURB curve (degree - 1)")

    def __repr__(self):
        return "{}(control_points={}, point_type={}, knot_vector={}, reverse={}, weights={})".format(
            self.__class__.__name__, repr(self.points),
            self.point_type, self.knot_vector, self.reverse, self.weights
        )

    def build_segment(self):
        # todo: implement
        pass

    def is_same_data(self, other):
        # todo: implement
        pass

    def copy_to(self, sketch):
        # todo: implement
        pass


class Bezier(Curve):
    """
    Bezier curve segment.
    """

    def __init__(self, sketch, points, reverse=False):
        Curve.__init__(self, sketch, points, reverse=reverse)

    @staticmethod
    def from_wdb(sketch, data, reverse):
        data = librt.cast(data, librt.POINTER(librt.struct_bezier_seg)).contents
        return Bezier(
            sketch,
            points=[data.ctl_points[i] for i in xrange(0, data.degree + 1)],
            reverse=reverse
        )

    degree = property(fget=lambda self: len(self.points) - 1, doc="degree of curve (number of control points - 1)")

    def __repr__(self):
        return "{}(control_points={}, reverse={})".format(
            self.__class__.__name__, repr(self.points), self.reverse
        )

    def build_segment(self):
        # todo: implement
        pass

    def is_same_data(self, other):
        # todo: implement
        pass

    def copy_to(self, sketch):
        # todo: implement
        pass


class Sketch(Primitive, collections.MutableSequence):

    def __init__(self, name, base=(0, 0, 0), u_vec=(1, 0, 0), v_vec=(0, 1, 0), vertices=None, curves=None, copy=False):
        Primitive.__init__(self, name=name)
        self.base = Vector(base, copy=copy)
        self.u_vec = Vector(u_vec, copy=copy)
        self.v_vec = Vector(v_vec, copy=copy)
        if vertices is None:
            vertices = []
        elif not isinstance(vertices, list):
            vertices = list(vertices)
        for i in range(0, len(vertices)):
            vertices[i] = Vector(vertices[i], copy=copy)
        self.vertices = vertices
        if curves is None:
            curves = []
        elif not isinstance(curves, list):
            curves = list(curves)
        self.curves = curves
        for i in xrange(0, len(curves)):
            self.add_curve_segment(curves[i], segment_index=i, copy=copy)

    def __repr__(self):
        return "{}({}, base={}, u_vec={}, v_vec={} curves={})".format(
            self.__class__.__name__, self.name, repr(self.base), repr(self.u_vec), repr(self.v_vec), repr(self.curves)
        )

    def vertex_index(self, value, copy=False):
        vertex_count = len(self.vertices)
        if isinstance(value, numbers.Integral):
            if value > vertex_count - 1:
                raise ValueError("Invalid vertex index: {}".format(value))
            return value
        value = Vector(value, copy=copy)
        if len(value) != 2:
            raise ValueError("Sketches need 2D vertexes, but got: {}".format(value))
        for i in xrange(0, vertex_count):
            if self.vertices[i].is_same(value):
                return i
        self.vertices.append(value)
        return vertex_count

    def _parse_curve_segment(self, *args, **kwargs):
        index = kwargs.get("index")
        if len(args) == 1 and isinstance(args[0], Curve):
            # if the curve is part of another sketch, or the curve is
            # already there on a different index, we need to copy it
            copy_needed = args[0].sketch != self
            if not copy_needed:
                try:
                    former_index = self.curves.index(args[0])
                except ValueError:
                    former_index = None
                copy_needed = (former_index and former_index != index)
            return args[0].copy_to(self) if copy_needed else args[0]
        elif len(args) == 2:
            curve_type = Curve.TYPE_MAP[args[0]]
            if curve_type:
                return curve_type(self, args[1], **kwargs)
        elif len(args) == 1 and isinstance(args[0], dict):
            kwargs.update(args[0])
            curve_type = kwargs.get("curve_type")
            points = kwargs.get("points", [])
            if curve_type is not None:
                curve_type = Curve.TYPE_MAP[curve_type]
                if curve_type:
                    return curve_type(self, points, **kwargs)
        raise ValueError("Cant parse sketch curve segment from params: args={}, kwargs={}".format(args, kwargs))

    def set_curve_segment(self, index, *args, **kwargs):
        kwargs["index"] = index
        self.curves[index] = self._parse_curve_segment(*args, **kwargs)

    def add_curve_segment(self, *args, **kwargs):
        self.curves.append(self._parse_curve_segment(*args, **kwargs))

    def insert_curve_segment(self, index, *args, **kwargs):
        kwargs["index"] = index
        self.curves.insert(index, self._parse_curve_segment(*args, **kwargs))

    def __len__(self):
        return len(self.curves)

    def __delitem__(self, index):
        del self.curves[index]

    def __setitem__(self, index, value):
        self.set_curve_segment(index, value)

    def __getitem__(self, index):
        return self.curves[index]

    def insert(self, index, value):
        self.insert_curve_segment(index, value)

    def build_curves(self):
        ci = librt.struct_rt_curve()
        ci.count = len(self.curves)
        if ci.count:
            ci.reverse = (librt.c_int * ci.count)()
            ci.segment = (librt.genptr_t * ci.count)()
        else:
            ci.reverse = None
            ci.segment = None
        for i in xrange(0, ci.count):
            curve = self.curves[i]
            ci.reverse[i] = bool(curve.reverse)
            ci.segment[i] = librt.cast(librt.pointer(curve.build_segment()), librt.c_void_p)
        return ci, self.vertices

    def update_params(self, params):
        params.update({
            "sketch": self,
        })

    def copy(self):
        return Sketch(self.name, self.curves, copy=True)

    def has_same_data(self, other):
        curve_count = len(self.curves)
        if len(other.curves) != curve_count:
            return False
        return all([self.curves[i].is_same(other.curves[i]) for i in xrange(0, curve_count)])

    def line(self, start, end, reverse=False, copy=False):
        return Line(self, [start, end], reverse=reverse, copy=copy)

    def arc(self, start, end, radius, reverse=False, center_is_left=False, clock_wise=False, copy=False):
        return CircularArc(
            self, [start, end], reverse=reverse, radius=radius,
            center_is_left=center_is_left, clock_wise=clock_wise, copy=copy
        )

    def circle(self, point, center, clock_wise=False, copy=False):
        return CircularArc(self, [point, center], clock_wise=clock_wise, copy=copy)

    def nurb(self, points, reverse=False, point_type=None, knot_vector=None, weights=None, copy=False):
        return NURB(
            self, points, reverse=reverse, point_type=point_type, knot_vector=knot_vector, weights=weights, copy=copy
        )

    def bezier(self, points, reverse=False):
        return Bezier(self, points, reverse= reverse)

    @staticmethod
    def example_sketch():
        example = Sketch("example.s")
        example.add_curve_segment(example.circle((0.5, 0), (0, 0)))
        example.add_curve_segment(example.line((-1, -1), (-1, 1)))
        example.add_curve_segment(example.line((-1, 1), (1, 1)))
        example.add_curve_segment(example.line((1, 1), (1, -1)))
        example.add_curve_segment(example.line((1, -1), (-1, -1)))
        return example

    @staticmethod
    def from_wdb(name, data):
        vertices = []
        for i in xrange(0, data.vert_count):
            vertices.append(Vector(data.verts[i]))
        result = Sketch(
            name=name, base=Vector(data.V), u_vec=Vector(data.u_vec), v_vec=Vector(data.v_vec), vertices=vertices
        )
        result.data = data
        curves = data.curve
        for i in xrange(0, curves.count):
            curve = curves.segment[i]
            magic = librt.cast(curve, librt.POINTER(librt.struct_line_seg)).contents.magic
            reverse = bool(curves.reverse[i])
            result.add_curve_segment(magic, curve, reverse=reverse)
        return result

Curve.TYPE_MAP = {
    "line": Line,
    librt.CURVE_LSEG_MAGIC: Line.from_wdb,
    Line: Line,
    "carc": CircularArc,
    librt.CURVE_CARC_MAGIC: CircularArc.from_wdb,
    CircularArc: CircularArc,
    "nurb": NURB,
    librt.CURVE_NURB_MAGIC: NURB.from_wdb,
    NURB: NURB,
    "bezier": Bezier,
    librt.CURVE_BEZIER_MAGIC: Bezier.from_wdb,
    Bezier: Bezier,
}


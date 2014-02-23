"""
Python wrapper for the Sketch primitive of BRL-CAD.
"""

from base import Primitive
from brlcad.util import indexed_getter, indexed_setter
from brlcad.vmath import Vector
import brlcad._bindings.librt as librt


class Curve(object):
    """
    Represents one curve segment of a sketch.
    """

    def __init__(self, sketch, points, reverse=False, copy=False):
        self.sketch = sketch
        # todo: look up points if not index
        self.points = list(points) if copy else points
        self.reverse = reverse


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

    start = property(fget=indexed_getter("points", 0), fset=indexed_setter("points", 0))
    end = property(fget=indexed_getter("points", 1), fset=indexed_setter("points", 1))

    def __repr__(self):
        return "{}(start={}, end={})".format(
            self.__class__.__name__, self.sketch.vertices[self.start], self.sketch.vertices[self.end]
        )


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

    start = property(fget=indexed_getter("points", 0), fset=indexed_setter("points", 0))
    end = property(fget=indexed_getter("points", 1), fset=indexed_setter("points", 1))

    def __repr__(self):
        return "{}(start={}, end={}, radius={}, reverse={}, center_is_left={}, clock_wise={})".format(
            self.__class__.__name__, self.sketch.vertices[self.start], self.sketch.vertices[self.end],
            self.radius, self.reverse, self.center_is_left, self.clock_wise
        )


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
            points=[data.ctl_points[i] for i in range(0, data.c_size)],
            reverse=reverse,
            point_type=data.pt_type,
            knot_vector=data.k,
            weights=[data.weights[i] for i in range(0, data.c_size)]
        )

    degree = property(fget=lambda self: len(self.points) - 1, doc="degree of curve (number of control points - 1)")

    order = property(fget=lambda self: len(self.points) - 2, doc="order of NURB curve (degree - 1)")

    def __repr__(self):
        return "{}(control_points={}, point_type={}, knot_vector={}, reverse={}, weights={})".format(
            self.__class__.__name__,
            [self.sketch.vertices[i] for i in self.points],
            self.point_type, self.knot_vector, self.reverse, self.weights
        )

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
            points=[data.ctl_points[i] for i in range(0, data.degree + 1)],
            reverse=reverse
        )

    degree = property(fget=lambda self: len(self.points) - 1, doc="degree of curve (number of control points - 1)")

    def __repr__(self):
        return "{}(control_points={}, reverse={})".format(
            self.__class__.__name__, [self.sketch.vertices[i] for i in self.points], self.reverse
        )


class Sketch(Primitive):

    def __init__(self, name, base=(0, 0, 0), u_vec=(1, 0, 0), v_vec=(0, 1, 0), vertices=None, curves=None, copy=False):
        Primitive.__init__(self, name=name)
        self.base = base
        self.u_vec = u_vec
        self.v_vec = v_vec
        self.vertices = vertices if vertices is not None else []
        self.curves = curves if curves is not None else []
        if copy or not vertices:
            for x in curves:
                self.add_curve_segment(x, copy=copy)

    def __repr__(self):
        return "{}({}, base={}, u_vec={}, v_vec={} curves={})".format(
            self.__class__.__name__, self.name, repr(self.base), repr(self.u_vec), repr(self.v_vec), repr(self.curves)
        )

    def add_curve_segment(self, *args, **kwargs):
        copy = kwargs.get("copy", False)
        if len(args) == 1 and isinstance(args[0], Curve):
            if args[0].sketch == self and not copy:
                return
            else:
                self.curves.append(args[0].copy_to(self))
                return
        elif len(args) == 2:
            curve_type = Curve.TYPE_MAP[args[0]]
            if curve_type:
                self.curves.append(curve_type(self, args[1], **kwargs))
                return
        raise ValueError("Cant parse sketch curve segment from params: args={}, kwargs={}".format(args, kwargs))

    def build_curves(self):
        ci = librt.struct_rt_curve()
        ci.count = len(self.curves)
        ci.reverse = librt.c_int * ci.count
        ci.segment = librt.genptr_t * ci.count
        for i in range(0, ci.count):
            curve = self.curves[i]
            ci.reverse[i] = bool(curve.reverse)
            ci.segment[i] = curve.build_segment()
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
        return all([self.curves[i].is_same(other.curves[i]) for i in range(0, curve_count)])

    @staticmethod
    def from_wdb(name, data):
        vertices = []
        for i in range(0, data.vert_count):
            vertices.append(Vector(data.verts[i]))
        result = Sketch(
            name=name, base=Vector(data.V), u_vec=Vector(data.u_vec), v_vec=Vector(data.v_vec), vertices=vertices
        )
        result.data = data
        curves = data.curve
        for i in range(0, curves.count):
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
    "arc": CircularArc,
    librt.CURVE_CARC_MAGIC: CircularArc.from_wdb,
    CircularArc: CircularArc,
    "nurb": NURB,
    librt.CURVE_NURB_MAGIC: NURB.from_wdb,
    NURB: NURB,
    "bezier": Bezier,
    librt.CURVE_BEZIER_MAGIC: Bezier.from_wdb,
    Bezier: Bezier,
}


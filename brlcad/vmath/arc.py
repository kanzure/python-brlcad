"""
Math related to geometry features of circular arcs.
"""
import math
from brlcad.vmath import Vector, Triangle
import numpy as np


class CalculatingType(object):
    """
    This is a singleton used to mark fields of the arc which are
    currently calculating, to avoid infinite recursion as we
    calculate arc elements which depend on each other but can
    be calculated from alternative elements.
    """
    def __repr__(self):
        return "Calculating"

Calculating = CalculatingType()

_ARC_CALC_FUNCTION_MAP = dict()


def _create_getter(name, calc_func=None):
    """
    Creates getter functions for the calculated properties of an arc.
    The returned function wraps the passed in <calc_func> which will
    be used to calculate the value of the property. The calculated
    value is only calculated once and cached for further access.
    It also populates the _ARC_CALC_FUNCTION_MAP which allows
    programmatic access to the parameter calculation functions.
    """
    def getter(self):
        value = self._props.get(name)
        if value is Calculating:
            return None
        if value is None:
            self._props[name] = Calculating
            if calc_func:
                value = calc_func(self)
            else:
                raise ValueError(
                    "Mandatory parameter <{}> missing for: {}".format(name, self)
                )
            if value is None:
                raise ValueError(
                    "Not enough information to calculate <{}> for: {}".format(name, self)
                )
            self._props[name] = value
        return value
    _ARC_CALC_FUNCTION_MAP[name] = calc_func
    return getter


# noinspection PyPropertyAccess
class Arc(object):

    _param_wrappers = {
        "angle": float,
        "apex": Vector.wrap,
        "arc_height": Vector.wrap,
        "arc_height_unit": Vector.wrap,
        "arc_point": Vector.wrap,
        "d_origin": float,
        "end_point": Vector.wrap,
        "end_radius": Vector.wrap,
        "end_radius_unit": Vector.wrap,
        "end_tangent": Vector.wrap,
        "height": float,
        "length": float,
        "mid_point": Vector.wrap,
        "origin": Vector.wrap,
        "plane_normal": Vector.wrap,
        "radius": float,
        "secant": Vector.wrap,
        "secant_unit": Vector.wrap,
        "start_point": Vector.wrap,
        "start_radius": Vector.wrap,
        "start_radius_unit": Vector.wrap,
        "start_tangent": Vector.wrap,
    }

    def __init__(self, verify=False, **kwargs):
        """
        Create an arc based on one of many possible parameter sets.
        The following combinations are accepted:
        * (start_point, end_point/secant, angle, plane_normal)
        * (start_point, angle, origin, plane_normal)
        * (start_point, end_point/secant, origin, plane_normal)
        * (start_point, end_point/secant, arc_height)
        * (start_point, end_point/secant, arc_point)
        If some extra parameters are already available, and checking is required,
        use verify=True (default is False, meaning parameters are not checked for consistency).
        Parameters which are not set will be calculated if needed, but at least one of
        the above mentioned combinations must be provided completely.
        """
        # parse parameters from possibly raw input:
        self._props = dict()
        self._wrap_params(kwargs)
        # verify parameter consistency
        if verify:
            self.verify()

    @staticmethod
    def wrap_param(param_name, value):
        """
        Wraps/parses the given parameter with/to the expected type.
        For example a Vector parameter will be wrapped using:
        Vector.wrap(value),
        a float parameter will be wrapped using:
        float(value)

        This approach allows passing in parameters which can be of
        any type accepted by those wrappers, e.g. a string of comma
        separated numbers is a valid value for a Vector parameter.
        """
        wrapper = Arc._param_wrappers[param_name]
        if value is not None:
            value = wrapper(value)
        return value

    def _wrap_params(self, params):
        unknown_params = set(params.keys()).difference(Arc._param_wrappers.keys())
        if unknown_params:
            raise ValueError("Unknown Arc parameters: {}".format(unknown_params))
        for param_name, value in params.items():
            self._props[param_name] = self.wrap_param(param_name, value)

    def _is_set(self, param_name):
        value = self._props.get(param_name)
        return value is not None and value is not Calculating

    def verify(self):
        if self.start_point is None:
            raise ValueError("<start_point> must be provided for an Arc")
        verified_props = (
            self.start_point, self.end_point, self.secant, self.origin,
            self.angle, self.plane_normal, self.arc_height
        )
        if verified_props.count(None) > 0:
            raise ValueError(
                "Parameter set is not complete to fully define an arc: {}".format(self)
            )
        crt_props = dict(self._props)
        for param_name, crt_value in crt_props.items():
            calc_func = _ARC_CALC_FUNCTION_MAP.get(param_name)
            if calc_func is not None:
                calculated_value = calc_func(self)
                if not np.allclose(crt_value, calculated_value):
                    raise ValueError(
                        "Verify failed for {}, expected: {} but got {}".format(
                            param_name, calculated_value, crt_value
                        )
                    )

    def __repr__(self):
        return "{}(**{})".format(self.__class__.__name__, self._props)

    # Property declarations/calculation functions

    start_point = property(fget=_create_getter("start_point"), doc="Start point of the arc")

    def _calculate_start_tangent(self):
        plane_normal = self.plane_normal
        start_radius = self.start_radius
        if plane_normal is not None and start_radius is not None:
            return plane_normal.cross(start_radius)
        return None

    start_tangent = property(fget=_create_getter("start_tangent", _calculate_start_tangent),
                             doc="The tangent (of <radius> length) to the arc at <start_point>.")

    def _calculate_start_tangent_unit(self):
        start_tangent = self.start_tangent
        if start_tangent is not None:
            return start_tangent.assure_normal("<start_tangent> of zero length")
        return None

    start_tangent_unit = property(fget=_create_getter("start_tangent", _calculate_start_tangent_unit),
                                  doc="The unit vector tangent to the arc at <start_point>")

    def _calculate_start_radius(self):
        origin = self.origin
        if origin is not None:
            return self.start_point - origin
        return None

    start_radius = property(fget=_create_getter("start_radius", _calculate_start_radius),
                            doc="The vector pointing from <origin> to <start_point>")

    def _calculate_start_radius_unit(self):
        start_radius = self.start_radius
        if start_radius is not None:
            return start_radius.assure_normal("<start_radius> should be non-zero")
        return None

    start_radius_unit = property(fget=_create_getter("start_radius_unit", _calculate_start_radius_unit),
                                 doc="The unit vector pointing from <origin> to <start_point>")

    def _calculate_end_point(self):
        if self._is_set("secant"):
            secant = self.secant
            if secant is not None:
                return self.start_point + secant
        angle = self.angle
        start_radius = self.start_radius
        start_tangent = self.start_tangent
        if (angle, start_radius, start_tangent).count(None) == 0:
            return math.cos(angle) * start_radius + math.sin(angle) * start_tangent
        return None

    end_point = property(fget=_create_getter("end_point", _calculate_end_point),
                         doc="End point of the arc")

    def _calculate_end_tangent(self):
        plane_normal = self.plane_normal
        end_radius = self.end_radius
        if plane_normal is not None and end_radius is not None:
            return plane_normal.cross(end_radius)
        return None

    end_tangent = property(fget=_create_getter("end_tangent", _calculate_end_tangent),
                           doc="The tangent (of <radius> length) to the arc at <end_point>.")

    def _calculate_end_tangent_unit(self):
        end_tangent = self.end_tangent
        if end_tangent is not None:
            return end_tangent.assure_normal("<end_tangent> of zero length")
        return None

    end_tangent_unit = property(fget=_create_getter("end_tangent", _calculate_end_tangent_unit),
                                doc="The unit vector tangent to the arc at <end_point>")

    def _calculate_end_radius_unit(self):
        end_radius = self.end_radius
        if end_radius is not None:
            return end_radius.assure_normal("<end_radius> should be non-zero")
        return None

    end_radius_unit = property(fget=_create_getter("end_radius_unit", _calculate_end_radius_unit),
                               doc="The unit vector pointing from <origin> to <end_point>")

    def _calculate_end_radius(self):
        end_point = self.end_point
        if end_point is not None:
            return end_point - self.origin
        return None

    end_radius = property(fget=_create_getter("end_radius", _calculate_end_radius),
                          doc="The vector pointing from <origin> to <end_point>")

    def _calculate_secant(self):
        start_point = self.start_point
        end_point = self.end_point
        if start_point is not None and end_point is not None:
            return end_point - start_point
        return None

    secant = property(fget=_create_getter("secant", _calculate_secant),
                      doc="The secant vector pointing from <start_point> to <end_point>")

    def _calculate_secant_unit(self):
        secant = self.secant
        if secant is not None:
            return secant.assure_normal("<secant> must be non-zero")
        return None

    secant_unit = property(fget=_create_getter("secant_unit", _calculate_secant_unit),
                           doc="The unit vector pointing from <start_point> to <end_point>")

    def _calculate_length(self):
        secant = self.secant
        if secant is not None:
            return secant.norm()
        return None

    length = property(fget=_create_getter("length", _calculate_length),
                      doc="The length of the <secant> vector.")

    def _calculate_mid_point(self):
        end_point = self.end_point
        if end_point is not None:
            return (end_point + self.start_point) / 2.0
        return None

    mid_point = property(fget=_create_getter("mid_point", _calculate_mid_point),
                         doc="The mid-point between <start_point> and <end_point>")

    def _calculate_angle(self):
        start_point = self.start_point
        end_point = self.end_point
        if start_point is None or end_point is None:
            return None
        if self._is_set("arc_point"):
            arc_point = self._props["arc_point"]
        else:
            arc_point = self.apex
        if arc_point is not None:
            return self.central_angle(start_point=start_point, end_point=end_point, arc_point=arc_point)
        return None

    angle = property(fget=_create_getter("angle", _calculate_angle),
                     doc="The angle in radians between <start_radius> and <end_radius>. "
                         "It will be positive if it points clockwise when looking "
                         "in the direction of the plane-normal, negative otherwise.")

    def _calculate_plane_normal(self):
        if self._is_set("arc_point"):
            # this is not available as a property:
            arc_point = self._props["arc_point"]
        else:
            arc_point = self.apex
        start_point = self.start_point
        end_point = self.end_point
        if (arc_point, start_point, end_point).count(None) == 0:
            start_vector = start_point - arc_point
            end_vector = end_point - arc_point
            plane_normal = end_vector.cross(start_vector)
            plane_normal = plane_normal.assure_normal(
                "<arc_point>, <start_point>, <end_point> should not be collinear"
            )
            return plane_normal
        return None

    plane_normal = property(fget=_create_getter("plane_normal", _calculate_plane_normal),
                            doc="The unit vector normal to the arc's plane. "
                                "It's oriented so that the arc points clockwise from "
                                "<start_point> to <end_point> when looking "
                                "in the direction of the plane-normal.")

    def _calculate_radius(self):
        if not self._is_set("origin"):
            if self._is_set("arc_height"):
                height = self.height
                length = self.length
                if height is not None and length is not None:
                    return 0.5 * height + 0.125 * length * length / height
            if self._is_set("angle") or self._is_set("arc_point"):
                angle = self.angle
                length = self.length
                if angle is not None and length is not None:
                    return 0.5 * length / math.sin(0.5 * angle)
        start_radius = self.start_radius
        if start_radius is not None:
            return start_radius.norm()
        return None

    radius = property(fget=_create_getter("radius", _calculate_radius),
                      doc="The radius of the circle containing the arc.")

    def _calculate_origin(self):
        arc_height_unit = self.arc_height_unit
        height = self.height
        radius = self.radius
        mid_point = self.mid_point
        if (arc_height_unit, height, radius, mid_point).count(None) == 0:
            return mid_point + (height - radius) * arc_height_unit
        return None

    origin = property(fget=_create_getter("origin", _calculate_origin),
                      doc="The origin of the circle containing the arc.")

    def _calculate_arc_height_unit(self):
        if self._is_set("arc_height"):
            return self.arc_height.assure_normal("<arc_height> should be non-zero")
        plane_normal = self.plane_normal
        secant_unit = self.secant_unit
        if plane_normal is not None and secant_unit is not None:
            return secant_unit.cross(plane_normal)
        return None

    arc_height_unit = property(fget=_create_getter("arc_height_unit", _calculate_arc_height_unit),
                               doc="The unit vector parallel to the arc's height.")

    def _calculate_arc_height(self):
        height = self.height
        height_unit = self.arc_height_unit
        if height is not None and height_unit is not None:
            return height * height_unit
        return None

    arc_height = property(fget=_create_getter("arc_height", _calculate_arc_height),
                          doc="The arc's height vector pointing from <mid_point> to <height_point>.")

    def _calculate_height(self):
        if self._is_set("arc_height"):
            return self.arc_height.norm()
        radius = self.radius
        angle = self.angle
        if radius is not None and angle is not None:
            return radius * (1 - math.cos(0.5 * angle))
        return None

    height = property(fget=_create_getter("height", _calculate_height),
                      doc="The <arc_height> vector's length.")

    def _calculate_apex(self):
        if self._is_set("origin") and self._is_set("plane_normal"):
            radius = self.radius
            height_unit = self.arc_height_unit
            origin = self.origin
            if (radius, height_unit, origin).count(None) == 0:
                return origin + radius * height_unit
        mid_point = self.mid_point
        arc_height = self.arc_height
        if mid_point is not None and arc_height is not None:
            return mid_point + arc_height
        return None

    apex = property(fget=_create_getter("apex", _calculate_apex),
                    doc="The highest point on the arc, the farthest one from the <secant>. "
                        "It is placed at the intersection of the arc with <arc_height> vector, "
                        "at half-way on the arc between <start_point> and <end_point>")

    def _calculate_d_origin(self):
        radius = self.radius
        height = self.height
        if radius is not None and height is not None:
            return abs(radius - height)
        return None

    d_origin = property(fget=_create_getter("d_origin", _calculate_d_origin),
                        doc="The distance between the secant and <origin>."
                            "This is the length of the <origin> -> <mid_point> vector.")

    # Utility methods for calculating arc related geometry elements without creating an Arc object

    @staticmethod
    def central_angle(start_point, end_point, arc_point):
        """
        Calculates the measure in radians of the arc between <start_point> and <end_point>
        and containing <arc_point> in the circumscribed circle.

        The result is equal to the central angle (S-O-E).

        The inscribed angle S-A-E can be calculated as:

            angle(S-A-E) = pi - angle(S-O-E)/2

        On degenerate input (e.g. identical start/end/arc points) will raise ValueError.

                         A
                S _..-~~~+-._ E                  S _..-~~~--._ E
               ,-+           +-.                ,-+           +-.
             ,'   \         /   `.            ,'   \         /   `.
            /      \       /      \          /      \       /      \
           /        \angle/        \        /        \     /        \
          /          \.-./          \      /         ,\   /.         \
         ;            \ /            :    ;         /  \ /  \         :
         |             +             |    |        (    +    )        |
         :             O             ;    :         \   O   /         ;
          \                         /      \         `-----'         /
           \                       /        \         angle         /
            \                     /          \                     /
             `.                 ,'            `.                 ,'
               '-.          _.-'                '+.          _.-'
                  `'------''                    A  `'------''

        Notation:
            S -> start_point
            E -> end_point
            A -> arc_point
            angle -> result (expressed in radians)
        """
        inscribed_angle = Triangle.angle_from_points(start_point, arc_point, end_point)
        return 2.0 * (math.pi - inscribed_angle)

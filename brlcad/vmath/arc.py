"""
Math related to geometry features of circular arcs.
"""
import math
from brlcad.vmath import Vector, Triangle
from brlcad.vmath.geometry_object import GeometryObject, create_property


class Arc(GeometryObject):

    # Structures to be override from super-class:

    calc_function_map = dict()

    param_wrappers = {
        "arc_point": Vector.wrap,
    }

    canonical_init_params = {
        "start_point", "end_point", "angle", "plane_normal"
    }

    # end of structures to be overridden

    def __init__(self, verify=False, **kwargs):
        """
        Create an arc based on one of many possible parameter sets.
        The following combinations are accepted:
        * (start_point, end_point/secant, angle, plane_normal)
        * (start_point, angle, origin, plane_normal)
        * (start_point, end_point/secant, origin, plane_normal)
        * (start_point, length, reflex_angle, origin, plane_normal)
        * (start_point, end_point/secant, arc_height)
        * (start_point, end_point/secant, arc_point)
        If some extra parameters are already available, and checking is required,
        use verify=True (default is False, meaning parameters are not checked for consistency).
        Parameters which are not set will be calculated if needed, but at least one of
        the above mentioned combinations must be provided completely.
        """
        GeometryObject.__init__(self, verify=verify, **kwargs)

    # Property declarations/calculation functions

    start_point = create_property(
        name="start_point",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="Start point of the arc"
    )

    def _calculate_start_tangent(self):
        plane_normal = self.plane_normal
        start_radius = self.start_radius
        if plane_normal is not None and start_radius is not None:
            return plane_normal.cross(start_radius)
        return None

    start_tangent = create_property(
        name="start_tangent",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The tangent (of <radius> length) to the arc at <start_point>."
    )

    def _calculate_start_tangent_unit(self):
        start_tangent = self.start_tangent
        if start_tangent is not None:
            return start_tangent.assure_normal("<start_tangent> of zero length")
        return None

    start_tangent_unit = create_property(
        name="start_tangent_unit",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The unit vector tangent to the arc at <start_point>",
    )

    def _calculate_start_radius(self):
        origin = self.origin
        if origin is not None:
            return self.start_point - origin
        return None

    start_radius = create_property(
        name="start_radius",
        context=locals(),
        param_wrapper=Vector.wrap,
        doc="The vector pointing from <origin> to <start_point>"
    )

    def _calculate_start_radius_unit(self):
        start_radius = self.start_radius
        if start_radius is not None:
            return start_radius.assure_normal("<start_radius> should be non-zero")
        return None

    start_radius_unit = create_property(
        name="start_radius_unit",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The unit vector pointing from <origin> to <start_point>"
    )

    def _calculate_end_point(self):
        """
        Calculate the <end_point> from the available arc elements.
        When the secant is set, the calculation is trivial.
        If the <angle> or <length> is provided, the start_point is calculated
        based on the facts:

        O-E = O-P + P-E
        sin(pi - angle) = |P-E| / |O-E|
        cos(pi - angle) = |O-P| / |O-E|
        PE || start_tangent
                              _.------------.
                         ,--''               `---.
                      ,-'                         `-.
                    ,'                               `.
                  ,'                                   `.
                ,'                                       `.
             S /                     M                     \ E
              +..--------------------+--------------------_.+
             ;  `.`--.__             |              _..-'' / :
             ;    `-.   `--.__     angle      _..-''      /   :
            ;        `.       `--.._.-. _..-''           /    :
            |          `.           `+~:                /     |
            :            `.          O  `-.._          /      ;
             :             `.                ``-.__   /       ;
             :               `-.                   `-+._     ;
              \                 `.                  /P  ``-.+
               \                  `.               /       / A
                `.                  `.            /      ,'
                  `.                  `.         /     ,'
                    `.                  `-.     /    ,'
                      `-.                  `.  /  ,-'
                         `---.               ;+--'
                              `------------'' E'

        Given the above relations, the start-point can be calculated as:

            start_point = origin + cos(angle) * start_radius + sin(angle) * start_tangent

        If the end point E is not known, but the length S-E is known instead,
        the sin/cos can be calculated as:

            O-M / P-E = S-M / S-P = S-O / S-E

            S-P = S-M * S-E / S-O = (l/2) * l / r = l^2 / (2*r) = l * l / (2 * r)

            O-P = S-P - r = l^2 / (2*r) - r

            cos(angle) = - O-P / r = 1 - (l / r) * ( l / (2*r) )

            sin(angle) = sign * sqrt( 1 - cos^2(angle) )
                       = sign * (l / r) * sqrt( 1 - ( l / (2*r) )^2 ] )

            sign = -1 if reflex_angle else 1

        If reflex_angle is True, the end point is in E' instead of E,
        and sin(angle) will be negative.

        """
        if self.is_set("secant"):
            secant = self.secant
            if secant is not None:
                return self.start_point + secant
        start_radius = self.start_radius
        start_tangent = self.start_tangent
        origin = self.origin
        cos_angle = None
        sin_angle = None
        if self.is_set("length") and self.is_set("reflex_angle") and not self.is_set("angle"):
            radius = self.radius
            length = self.length
            reflex_angle = self.reflex_angle
            if radius is not None and length is not None:
                ratio = length / radius
                if ratio > 2.0:
                    raise ValueError(
                        "<length> {} should be less than <diameter> {}".format(
                            length, 2 * radius
                        )
                    )
                cos_angle = 1 - 0.5 * ratio * ratio
                sin_angle = math.sqrt(1 - cos_angle * cos_angle)
                if reflex_angle:
                    sin_angle = -sin_angle
        else:
            angle = self.angle
            if angle is not None:
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)
        if (sin_angle, cos_angle, start_radius, start_tangent).count(None) == 0:
            return origin + cos_angle * start_radius + sin_angle * start_tangent
        return None

    end_point = create_property(
        name="end_point",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="End point of the arc"
    )

    def _calculate_end_tangent(self):
        plane_normal = self.plane_normal
        end_radius = self.end_radius
        if plane_normal is not None and end_radius is not None:
            return plane_normal.cross(end_radius)
        return None

    end_tangent = create_property(
        name="end_tangent",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The tangent (of <radius> length) to the arc at <end_point>."
    )

    def _calculate_end_tangent_unit(self):
        end_tangent = self.end_tangent
        if end_tangent is not None:
            return end_tangent.assure_normal("<end_tangent> of zero length")
        return None

    end_tangent_unit = create_property(
        name="end_tangent_unit",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The unit vector tangent to the arc at <end_point>"
    )

    def _calculate_end_radius_unit(self):
        end_radius = self.end_radius
        if end_radius is not None:
            return end_radius.assure_normal("<end_radius> should be non-zero")
        return None

    end_radius_unit = create_property(
        name="end_radius_unit",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The unit vector pointing from <origin> to <end_point>"
    )

    def _calculate_end_radius(self):
        end_point = self.end_point
        if end_point is not None:
            return end_point - self.origin
        return None

    end_radius = create_property(
        name="end_radius",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The vector pointing from <origin> to <end_point>"
    )

    def _calculate_secant(self):
        start_point = self.start_point
        end_point = self.end_point
        if start_point is not None and end_point is not None:
            return end_point - start_point
        return None

    secant = create_property(
        name="secant",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The secant vector pointing from <start_point> to <end_point>"
    )

    def _calculate_secant_unit(self):
        secant = self.secant
        if secant is not None:
            return secant.assure_normal("<secant> must be non-zero")
        return None

    secant_unit = create_property(
        name="secant_unit",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The unit vector pointing from <start_point> to <end_point>"
    )

    def _calculate_length(self):
        secant = self.secant
        if secant is not None:
            return secant.norm()
        return None

    length = create_property(
        name="length",
        param_wrapper=float,
        context=locals(),
        doc="The length of the <secant> vector."
    )

    def _calculate_mid_point(self):
        end_point = self.end_point
        if end_point is not None:
            return (end_point + self.start_point) / 2.0
        return None

    mid_point = create_property(
        name="mid_point",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The mid-point between <start_point> and <end_point>"
    )

    def _calculate_angle(self):
        """
        Calculate the <angle> from the available arc elements.
        When the end point and one additional arc point is set,
        the calculation is done based on the triangle S-A-E and
        it's circumscribed circle, with the formula:

            angle(S-O-E) = 2 * ( pi - angle(S-A-E) )

        If the <length> and <reflex_angle> flag are provided,
        the <angle> is calculated based on the facts:

            angle = 2 * arcsin( l / (2 * r) )

        If reflex_angle:

            angle = 2 * pi - angle

                                            A
                              _.----~~~----,+._
                         ,-'''         _.-'._,.'-.
                      ,-'         __.-'  alpha `-.`-.
                    ,'        _.-'                `. `.
                  ,'     __.-'                      `. `.
                ,'   _.-'                             `. `.
             S /__.-'                M                  `-.\ E
              +:.--------------------+--------------------_:+
             ;   `:~-.__             |              _..-'' / :
             ;     `-.  `--.__     angle      _..-''      /   :
            ;         `.      `--.._.-. _..-''           /    :
            |           `.          :+~'                /     |
            :             `.      .' O\ `-.._          /      ;
             :              `.  .'     \     ``-.__   /       ;
             :                `+.       \          `-+       ;
              \               M' `.      \          /P      ;
               \                   `.     \        /       / A
                `.                   `.    \      /      ,'
                  `.                   `.   \    /     ,'
                    `.                   `-. \  /    ,'
                      `-.                   `.\/  ,-'
                         `-._                 _+-'
                             `'''---~~~----'''  E'

        """
        if self.is_set("reflex_angle"):
            reflex_angle = self.reflex_angle
            length = self.length
            radius = self.radius
            if (reflex_angle, length, radius).count(None) == 0:
                sin_angle = min(1, 0.5 * length / radius)
                angle = math.asin(sin_angle)
                if reflex_angle:
                    angle = math.pi - angle
                return 2 * angle
        start_point = self.start_point
        end_point = self.end_point
        if start_point is None or end_point is None:
            return None
        if self.is_set("arc_point"):
            arc_point = self._props["arc_point"]
        else:
            arc_point = self.apex
        if arc_point is not None:
            return self.central_angle(start_point=start_point, end_point=end_point, arc_point=arc_point)
        return None

    angle = create_property(
        name="angle",
        param_wrapper=float,
        context=locals(),
        doc="The angle in radians between <start_radius> and <end_radius>. "
            "It will be positive if it points clockwise when looking "
            "in the direction of the plane-normal, negative otherwise."
    )

    def _calculate_reflex_angle(self):
        angle = self.angle
        if angle is not None:
            return abs(angle) > math.pi
        return None

    reflex_angle = create_property(
        name="reflex_angle",
        param_wrapper=bool,
        context=locals(),
        doc="True for a reflex angle (absolute value > 180 degrees), False otherwise."
    )

    def _calculate_plane_normal(self):
        if self.is_set("arc_point"):
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

    plane_normal = create_property(
        name="plane_normal",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The unit vector normal to the arc's plane. "
            "It's oriented so that the arc points clockwise from "
            "<start_point> to <end_point> when looking "
            "in the direction of the plane-normal."
    )

    def _calculate_radius(self):
        if not self.is_set("origin"):
            if self.is_set("arc_height"):
                height = self.height
                length = self.length
                if height is not None and length is not None:
                    return 0.5 * height + 0.125 * length * length / height
            if self.is_set("angle") or self.is_set("arc_point"):
                angle = self.angle
                length = self.length
                if angle is not None and length is not None:
                    return 0.5 * length / math.sin(0.5 * angle)
        start_radius = self.start_radius
        if start_radius is not None:
            return start_radius.norm()
        return None

    radius = create_property(
        name="radius",
        param_wrapper=float,
        context=locals(),
        doc="The radius of the circle containing the arc."
    )

    def _calculate_diameter(self):
        radius = self.radius
        if radius is not None:
            return 2 * radius
        return None

    diameter = create_property(
        name="diameter",
        param_wrapper=float,
        context=locals(),
        doc="The diameter of the circle containing the arc."
    )

    def _calculate_origin(self):
        arc_height_unit = self.arc_height_unit
        height = self.height
        radius = self.radius
        mid_point = self.mid_point
        if (arc_height_unit, height, radius, mid_point).count(None) == 0:
            return mid_point + (height - radius) * arc_height_unit
        return None

    origin = create_property(
        name="origin",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The origin of the circle containing the arc."
    )

    def _calculate_arc_height_unit(self):
        if self.is_set("arc_height"):
            return self.arc_height.assure_normal("<arc_height> should be non-zero")
        plane_normal = self.plane_normal
        secant_unit = self.secant_unit
        if plane_normal is not None and secant_unit is not None:
            return secant_unit.cross(plane_normal)
        return None

    arc_height_unit = create_property(
        name="arc_height_unit",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The unit vector parallel to the arc's height."
    )

    def _calculate_arc_height(self):
        height = self.height
        height_unit = self.arc_height_unit
        if height is not None and height_unit is not None:
            return height * height_unit
        return None

    arc_height = create_property(
        name="arc_height",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The arc's height vector pointing from <mid_point> to <height_point>."
    )

    def _calculate_height(self):
        if self.is_set("arc_height"):
            return self.arc_height.norm()
        radius = self.radius
        angle = self.angle
        if radius is not None and angle is not None:
            return radius * (1 - math.cos(0.5 * angle))
        return None

    height = create_property(
        name="height",
        param_wrapper=float,
        context=locals(),
        doc="The <arc_height> vector's length."
    )

    def _calculate_apex(self):
        if self.is_set("origin") and self.is_set("plane_normal"):
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

    apex = create_property(
        name="apex",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The highest point on the arc, the farthest one from the <secant>. "
            "It is placed at the intersection of the arc with <arc_height> vector, "
            "at half-way on the arc between <start_point> and <end_point>"
    )

    def _calculate_d_origin(self):
        radius = self.radius
        height = self.height
        if radius is not None and height is not None:
            return abs(radius - height)
        return None

    d_origin = create_property(
        name="d_origin",
        param_wrapper=Vector.wrap,
        context=locals(),
        doc="The distance between the secant and <origin>."
            "This is the length of the <origin> -> <mid_point> vector."
    )

    # Utility methods for calculating arc related geometry elements without creating an Arc object

    @staticmethod
    def central_angle(start_point, end_point, arc_point):
        """
        Calculates the measure in radians of the arc between <start_point> and <end_point>
        and containing <arc_point> in the circumscribed circle.

        The result is equal to the central angle (S-O-E).

        The inscribed angle S-A-E can be calculated as:

            angle(S-A-E) = pi - angle(S-O-E) / 2

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

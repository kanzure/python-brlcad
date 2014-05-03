import unittest
import math
from brlcad.vmath import Arc
import brlcad.vmath.arc as p_arc
import numpy as np


class ArcTestCase(unittest.TestCase):

    arc_data = (
        {
            "start_point": "0, 1, -1",
            "end_point": "0, -1, -1",
            "plane_normal": "1, 0, 0",
            "angle": 3 * math.pi / 2,
            "origin": "0, 0, 0",
            "secant": "0, -2, 0",
            "length": 2.0,
            "reflex_angle": True,
            "arc_height": (0, 0, 1 + math.sqrt(2)),
            "arc_point": "0, 1, 1",
            "mid_point": "0, 0, -1",
            "apex": (0, 0, math.sqrt(2)),
            "radius": math.sqrt(2),
            "diameter": 2 * math.sqrt(2),
        },
        {
            "start_point": "0, 1, 1",
            "end_point": "0, -1, 1",
            "plane_normal": "1, 0, 0",
            "angle": math.pi / 2,
            "origin": "0, 0, 0",
            "secant": "0, -2, 0",
            "length": 2.0,
            "reflex_angle": False,
            "arc_height": (0, 0, math.sqrt(2) - 1),
            "arc_point": (0, math.sqrt(0.5), math.sqrt(1.5)),
            "mid_point": "0, 0, 1",
            "apex": (0, 0, math.sqrt(2)),
            "radius": math.sqrt(2),
            "diameter": 2 * math.sqrt(2),
        },
        {
            "start_point": "0, -1, 0",
            "end_point": (0, -1/math.sqrt(2), 1/math.sqrt(2)),
            "plane_normal": "-1, 0, 0",
            "angle": math.pi / 4,
            "origin": "0, 0, 0",
            "secant": (0, 1 - 1/math.sqrt(2), 1/math.sqrt(2)),
            "length": math.sqrt(2 - math.sqrt(2)),
            "reflex_angle": False,
            "arc_height": (
                0,
                0.5 * (1 + 1/math.sqrt(2)) - math.cos(math.pi / 8),
                math.sin(math.pi/8) - 0.5 / math.sqrt(2)
            ),
            "arc_point": (0,  -math.cos(math.pi / 6), math.sin(math.pi/6)),
            "mid_point": (0, -0.5 * (1 + 1/math.sqrt(2)), 0.5 / math.sqrt(2)),
            "apex": (0, -math.cos(math.pi / 8), math.sin(math.pi/8)),
            "radius": 1,
            "diameter": 2,
        },
    )

    base_arc_params = (
        ("start_point", "end_point", "angle", "plane_normal"),
        ("start_point", "secant", "angle", "plane_normal"),
        ("start_point", "angle", "origin", "plane_normal"),
        ("start_point", "end_point", "origin", "plane_normal"),
        ("start_point", "secant", "origin", "plane_normal"),
        ("start_point", "length", "reflex_angle", "origin", "plane_normal"),
        ("start_point", "end_point", "arc_height"),
        ("start_point", "secant", "arc_height"),
        ("start_point", "end_point", "arc_point"),
        ("start_point", "secant", "arc_point"),
    )

    def test_arc_from_base_params(self):
        for crt_data in self.arc_data:
            for param_names in self.base_arc_params:
                crt_params = dict([x for x in crt_data.items() if x[0] in param_names])
                arc = Arc(verify=False, **crt_params)
                print "******************************"
                print "param_names: ", param_names
                print "crt_params: ", crt_params
                print "******************************"
                print arc
                arc.verify()
                print arc
                for name, expected_value in crt_data.items():
                    if hasattr(arc, name):
                        expected_value = Arc.wrap_param(name, expected_value)
                        actual_value = getattr(arc, name)
                        self.assertTrue(
                            np.allclose(expected_value, actual_value),
                            msg="Wrong value for {}, expected: {}, found: {}".format(
                                name, expected_value, actual_value
                            )
                        )

    def test_arc_param_calculation(self):
        for crt_data in self.arc_data:
            for param_names in self.base_arc_params:
                crt_params = dict([x for x in crt_data.items() if x[0] in param_names])
                # noinspection PyProtectedMember
                for name in p_arc._ARC_CALC_FUNCTION_MAP:
                    arc = Arc(verify=False, **crt_params)
                    actual_value = getattr(arc, name)
                    if name in crt_data:
                        expected_value = Arc.wrap_param(name, crt_data[name])
                        self.assertTrue(
                            np.allclose(expected_value, actual_value),
                            msg="Wrong value for {}, expected: {}, found: {}".format(
                                name, expected_value, actual_value
                            )
                        )

    def test_unknown_param(self):
        name = 'wrong_param_for_arc'
        self.assertRaisesRegexp(
            expected_exception=ValueError,
            expected_regexp="Unknown Arc parameters.*{}".format(name),
            callable_obj=Arc,
            start_point="1,2,3",
            **{name: "some value"}
        )

    def test_central_angle(self):
        angle_checks = (
            ("1, 1, 1", "-1, -1, -1", "0.5, 0.5, 0.5", 0),
            ("1, 1, 1", "1, 1, 1", "2,2,2", 2.0 * math.pi),
            ("1, 0.5, 0.5", "-1, 1, 1", "0, 1.5, 1.5", math.pi),
            ([1.0/math.sqrt(2), 0.5, 0.5], "0, 0, 0.5", "0, 0, 0", 4*math.pi/3),
            ("0, 0, 0", "0, 0, 0.5", [1.0/math.sqrt(2), 0.5, 0.5], 5*math.pi/3),
        )
        for x in angle_checks:
            angle = Arc.central_angle(start_point=x[0], end_point=x[1], arc_point=x[2])
            self.assertAlmostEqual(
                x[3], angle, places=10,
                msg="Check failed for: {}; result is: {}".format(x, angle)
            )


if __name__ == "__main__":
    unittest.main()

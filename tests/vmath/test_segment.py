import unittest
from brlcad.vmath import Segment
import numpy as np


class SegmentTestCase(unittest.TestCase):

    segment_data = (
        {
            "start_point": "1, -2, 8",
            "end_point": "17, 13, -4",
            "delta": "16, 15, -12",
            "delta_unit": "0.64, 0.6, -0.48",
            "plane_normal": "0.64, 0.6, -0.48, -4.4",
            "length": 25,
            "mid_point": "9, 5.5, 2",
        },
    )

    base_segment_params = (
        ("start_point", "end_point"),
        ("start_point", "delta"),
        ("start_point", "delta_unit", "length"),
    )

    def test_segment_from_base_params(self):
        for crt_data in self.segment_data:
            for param_names in self.base_segment_params:
                crt_params = dict([x for x in crt_data.items() if x[0] in param_names])
                segment = Segment(verify=False, **crt_params)
                # print "******************************"
                # print "param_names: ", param_names
                # print "crt_params: ", crt_params
                # print "******************************"
                # print segment
                segment.verify()
                # print segment
                for name, expected_value in crt_data.items():
                    if hasattr(segment, name):
                        expected_value = Segment.wrap_param(name, expected_value)
                        actual_value = getattr(segment, name)
                        self.assertTrue(
                            np.allclose(expected_value, actual_value),
                            msg="Wrong value for {}, expected: {}, found: {}".format(
                                name, expected_value, actual_value
                            )
                        )

    def test_segment_param_calculation(self):
        for crt_data in self.segment_data:
            for param_names in self.base_segment_params:
                crt_params = dict([x for x in crt_data.items() if x[0] in param_names])
                for name in Segment.calc_function_map:
                    segment = Segment(verify=False, **crt_params)
                    actual_value = getattr(segment, name)
                    if name in crt_data:
                        expected_value = Segment.wrap_param(name, crt_data[name])
                        self.assertTrue(
                            np.allclose(expected_value, actual_value),
                            msg="Wrong value for {}, expected: {}, found: {}".format(
                                name, expected_value, actual_value
                            )
                        )

    def test_unknown_param(self):
        name = 'wrong_param_for_segment'
        self.assertRaisesRegexp(
            expected_exception=ValueError,
            expected_regexp="Unknown Segment parameters.*{}".format(name),
            callable_obj=Segment,
            start_point="1,2,3",
            **{name: "some value"}
        )


if __name__ == "__main__":
    unittest.main()

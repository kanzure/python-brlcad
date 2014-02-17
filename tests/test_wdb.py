import unittest
from brlcad.vmath import Vector

import brlcad.wdb as wdb
import brlcad.ctypes_adaptors as cta


class WDBTestCase(unittest.TestCase):

    def get_arb_checker(self, brl_db):
        def check_arb(name, expected_points):
            shape = brl_db.lookup_internal(name)
            expected = Vector(expected_points)
            if not expected.is_same(shape.points):
                self.fail("{0} != {1}".format(expected, shape.points))
        return check_arb

    def test_defaults(self):
        """
        Tests default values for primitive creation
        """
        with wdb.WDB("test_defaults.g", "BRL-CAD geometry for testing wdb defaults") as brl_db:
            brl_db.sphere("sphere.s")
            brl_db.rpp("rpp.s")
            brl_db.wedge("wedge.s")
            brl_db.arb4("arb4.s")
            brl_db.arb5("arb5.s")
            brl_db.arb6("arb6.s")
            brl_db.arb7("arb7.s")
            brl_db.arb8("arb8.s")
            brl_db.ellipsoid("ellipsoid.s")
            brl_db.torus("torus.s")
            brl_db.rcc("rcc.s")
            brl_db.tgc("tgc.s")
            brl_db.cone("cone.s")
            brl_db.trc("trc.s")
            brl_db.trc_top("trc_top.s")
            brl_db.rpc("rpc.s")
            brl_db.rhc("rhc.s")
            brl_db.epa("epa.s")
            brl_db.ehy("ehy.s")
            brl_db.hyperboloid("hyperboloid.s")
            brl_db.eto("eto.s")
            brl_db.arbn("arbn.s")
            brl_db.particle("particle.s")
            brl_db.pipe("pipe.s")
        with wdb.WDB("test_defaults.g") as brl_db:
            check_arb = self.get_arb_checker(brl_db)
            check_arb("wedge.s", "0, 0, 0, 1, 0, 0, 1, -1, 0, 0, -1, 0, 0, 0, 1, 0.5, 0, 1, 0.5, -1, 1, 0, -1, 1")
            check_arb("arb4.s", "0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1")
            check_arb("arb5.s", "1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1")
            check_arb("arb6.s", "1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 1, 0, 1, 1, 0, 1, -1, 0, 1, -1, 0, 1")
            check_arb("arb7.s", "1, 1, -1, 1, -1, -1, -3, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, 1, 1")
            check_arb("arb8.s", "1, 1, -1, 1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1")
            shape = brl_db.lookup_internal("arbn.s")
            expected = Vector((1, 0, 0, 1, -1, 0, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 0, 1, 1, 0, 0, -1, 1))
            self.assertTrue(expected.is_same(cta.flatten_floats(shape.planes)))
            shape = brl_db.lookup_internal("sphere.s")
            self.assertTrue(shape.center.is_same((0, 0, 0)))
            self.assertEqual(1, shape.radius)
            shape = brl_db.lookup_internal("ellipsoid.s")
            self.assertTrue(shape.center.is_same((0, 0, 0)))
            self.assertEqual(1, shape.radius)
            self.assertTrue(shape.a.is_same((1, 0, 0)))
            self.assertTrue(shape.b.is_same((0, 1, 0)))
            self.assertTrue(shape.c.is_same((0, 0, 1)))


if __name__ == "__main__":
    unittest.main()

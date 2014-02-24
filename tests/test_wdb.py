import os
import unittest

from brlcad.vmath import Vector
import brlcad.wdb as wdb
import brlcad.ctypes_adaptors as cta
import brlcad.primitives as primitives


class WDBTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create the test DB:
        if os.path.isfile("test_defaults.g"):
            os.remove("test_defaults.g")
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
            brl_db.rpc("rpc.s")
            brl_db.rhc("rhc.s")
            brl_db.epa("epa.s")
            brl_db.ehy("ehy.s")
            brl_db.hyperboloid("hyperboloid.s")
            brl_db.eto("eto.s")
            brl_db.arbn("arbn.s")
            brl_db.particle("particle.s")
            brl_db.pipe("pipe.s")
            test_comb = primitives.Combination(name="combination.c")
            for shape_name in brl_db.ls():
                test_comb.tree.add_child(shape_name)
            brl_db.save(test_comb)
        # load the DB and cache it in a class variable:
        cls.brl_db = wdb.WDB("test_defaults.g")

    @classmethod
    def tearDownClass(cls):
        # close the test DB
        cls.brl_db.close()
        # delete the test DB except the DEBUG_TESTS environment variable is set
        if not os.environ.get("DEBUG_TESTS", False):
            os.remove("test_defaults.g")

    def lookup_shape(self, name):
        return self.brl_db.lookup(name)

    def check_arb(self, name, expected_points):
        shape = self.lookup_shape(name)
        expected = Vector(expected_points)
        if not expected.is_same(shape.points):
            self.fail("{0} != {1}".format(expected, shape.points))

    def check_tgc(self, name, expected_points):
        shape = self.lookup_shape(name)
        expected = Vector(expected_points)
        actual = cta.flatten_numbers([shape.base, shape.height, shape.a, shape.b, shape.c, shape.d])
        if not expected.is_same(actual):
            self.fail("{0} != {1}".format(expected, actual))

    def test_rpp_defaults(self):
        self.check_arb("rpp.s", "1, -1, -1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1")

    def test_wedge_defaults(self):
        self.check_arb("wedge.s", "0, 0, 0, 1, 0, 0, 1, -1, 0, 0, -1, 0, 0, 0, 1, 0.5, 0, 1, 0.5, -1, 1, 0, -1, 1")

    def test_arb4_defaults(self):
        self.check_arb("arb4.s", "0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1")

    def test_arb5_defaults(self):
        self.check_arb("arb5.s", "1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1")

    def test_arb6_defaults(self):
        self.check_arb("arb6.s", "1, 1, 0, 1, -1, 0, -1, -1, 0, -1, 1, 0, 1, 0, 1, 1, 0, 1, -1, 0, 1, -1, 0, 1")

    def test_arb7_defaults(self):
        self.check_arb(
            "arb7.s",
            "1, 1, -1, 1, -1, -1, -3, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, 1, 1"
        )

    def test_arb8_defaults(self):
        self.check_arb("arb8.s", "1, 1, -1, 1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1")

    def test_arbn_defaults(self):
        shape = self.lookup_shape("arbn.s")
        expected = Vector((1, 0, 0, 1, -1, 0, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 0, 1, 1, 0, 0, -1, 1))
        self.assertTrue(expected.is_same(cta.flatten_numbers(shape.planes)))

    def test_sphere_defaults(self):
        shape = self.lookup_shape("sphere.s")
        self.assertTrue(shape.center.is_same((0, 0, 0)))
        self.assertEqual(1, shape.radius)

    def test_ellipsoid_defaults(self):
        shape = self.lookup_shape("ellipsoid.s")
        self.assertTrue(shape.center.is_same((0, 0, 0)))
        self.assertEqual(1, shape.radius)
        self.assertTrue(shape.a.is_same((1, 0, 0)))
        self.assertTrue(shape.b.is_same((0, 1, 0)))
        self.assertTrue(shape.c.is_same((0, 0, 1)))

    def test_rpc_defaults(self):
        shape = self.lookup_shape("rpc.s")
        self.assertTrue(shape.base.is_same((0, 0, 0)))
        self.assertTrue(shape.height.is_same((-1, 0, 0)))
        self.assertTrue(shape.breadth.is_same((0, 0, 1)))
        self.assertEqual(0.5, shape.half_width)

    def test_rhc_defaults(self):
        shape = self.lookup_shape("rhc.s")
        self.assertTrue(shape.base.is_same((0, 0, 0)))
        self.assertTrue(shape.height.is_same((-1, 0, 0)))
        self.assertTrue(shape.breadth.is_same((0, 0, 1)))
        self.assertEqual(0.5, shape.half_width)
        self.assertEqual(0.1, shape.asymptote)

    def test_rcc_defaults(self):
        self.check_tgc("rcc.s", "0, 0, 0, 0, 0, 1, 0, -1, 0, -1, 0, 0, 0, -1, 0, -1, 0, 0")

    def test_tgc_defaults(self):
        self.check_tgc("tgc.s", "0, 0, 0, 0, 0, 1, 0, 1, 0, 0.5, 0, 0, 0, 0.5, 0, 1, 0, 0")

    def test_cone_defaults(self):
        self.check_tgc("cone.s", "0, 0, 0, 0, 0, 1, 0, -1, 0, 1, 0, 0, 0, -0.5, 0, 0.5, 0, 0")

    def test_trc_defaults(self):
        self.check_tgc("trc.s", "0, 0, 0, 0, 0, 1, 0, -1, 0, -1, 0, 0, 0, -0.5, 0, -0.5, 0, 0")

    def test_torus_defaults(self):
        shape = self.lookup_shape("torus.s")
        self.assertTrue(shape.center.is_same((0, 0, 0)))
        self.assertTrue(shape.n.is_same((0, 0, 1)))
        self.assertEqual(1, shape.r_revolution)
        self.assertEqual(0.2, shape.r_cross)

    def test_eto_defaults(self):
        shape = self.lookup_shape("eto.s")
        self.assertTrue(shape.center.is_same((0, 0, 0)))
        self.assertTrue(shape.n.is_same((0, 0, 1)))
        self.assertTrue(shape.s_major.is_same((0, 0.5, 0.5)))
        self.assertEqual(1, shape.r_revolution)
        self.assertEqual(0.2, shape.r_minor)

    def test_epa_defaults(self):
        shape = self.lookup_shape("epa.s")
        self.assertTrue(shape.base.is_same((0, 0, 0)))
        self.assertTrue(shape.height.is_same((0, 0, 1)))
        self.assertTrue(shape.n_major.is_same((0, 1, 0)))
        self.assertEqual(1, shape.r_major)
        self.assertEqual(0.5, shape.r_minor)

    def test_ehy_defaults(self):
        shape = self.lookup_shape("ehy.s")
        self.assertTrue(shape.base.is_same((0, 0, 0)))
        self.assertTrue(shape.height.is_same((0, 0, 1)))
        self.assertTrue(shape.n_major.is_same((0, 1, 0)))
        self.assertEqual(1, shape.r_major)
        self.assertEqual(0.5, shape.r_minor)
        self.assertEqual(0.1, shape.asymptote)

    def test_hyperboloid_defaults(self):
        shape = self.lookup_shape("hyperboloid.s")
        self.assertTrue(shape.base.is_same((0, 0, 0)))
        self.assertTrue(shape.height.is_same((0, 0, 1)))
        self.assertTrue(shape.a_vec.is_same((0, 1, 0)))
        self.assertEqual(0.5, shape.b_mag)
        self.assertEqual(0.2, shape.base_neck_ratio)

    def test_particle_defaults(self):
        shape = self.lookup_shape("particle.s")
        self.assertTrue(shape.base.is_same((0, 0, 0)))
        self.assertTrue(shape.height.is_same((0, 0, 1)))
        self.assertEqual(0.5, shape.r_base)
        self.assertEqual(0.2, shape.r_end)

    def test_pipe_defaults(self):
        shape = self.lookup_shape("pipe.s")
        expected = primitives.Pipe("pipe.s")
        self.assertTrue(expected.is_same(shape))

    def test_save_primitives(self):
        test_shape_name = "test_save.s"
        for shape_name in self.brl_db.ls():
            shape = self.lookup_shape(shape_name)
            if isinstance(shape, primitives.Combination):
                continue
            shape = shape.copy()
            shape.name = test_shape_name
            expected = shape.copy()
            self.brl_db.save(shape)
            shape = self.lookup_shape(test_shape_name)
            self.assertTrue(expected.is_same(shape))
        self.brl_db.delete(test_shape_name)

    def test_save_pipe(self):
        shape = self.lookup_shape("pipe.s")
        shape.append_point((0, 2, 2), 0.5, 0.3, 0.8)
        for i in range(0, len(shape.points)):
            shape.points[i].r_bend = 0.8
        expected = shape.copy()
        self.brl_db.save(shape)
        shape = self.lookup_shape("pipe.s")
        self.assertTrue(expected.is_same(shape))

    def test_lookup_not_existing(self):
        self.assertIsNone(self.lookup_shape("not_existing"))

    def test_delete_not_existing(self):
        self.assertFalse(self.brl_db.delete("not_existing"))

    def test_delete_shape(self):
        shape_name = "created_to_be_deleted.s"
        self.brl_db.sphere(shape_name)
        self.assertIsNotNone(self.lookup_shape(shape_name))
        self.assertTrue(self.brl_db.delete(shape_name))
        self.assertIsNone(self.lookup_shape(shape_name))

    def test_save_combination(self):
        test_comb = self.lookup_shape("combination.c")
        expected = test_comb.copy()
        del expected.tree[0]
        test_name = "test_save.c"
        expected.name = test_name
        self.brl_db.save(expected)
        test_comb = self.lookup_shape(test_name)
        self.assertTrue(expected.is_same(test_comb))
        self.brl_db.delete(test_name)


if __name__ == "__main__":
    unittest.main()

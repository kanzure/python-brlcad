import os
import unittest
from brlcad.primitives import Sketch

import brlcad.wdb as wdb


class SketchTestCase(unittest.TestCase):

    TEST_FILE_NAME = "test_sketch.g"

    DEBUG_TESTS = "DEBUG_TESTS"

    @classmethod
    def setUpClass(cls):
        # create the test DB:
        if os.path.isfile(cls.TEST_FILE_NAME):
            os.remove(cls.TEST_FILE_NAME)
        with wdb.WDB(cls.TEST_FILE_NAME, "BRL-CAD geometry for testing sketch primitive") as brl_db:
            brl_db.sketch("sketch.s")
        # load the DB and cache it in a class variable:
        cls.brl_db = wdb.WDB(cls.TEST_FILE_NAME)

    @classmethod
    def tearDownClass(cls):
        # close the test DB
        cls.brl_db.close()
        # delete the test DB except the DEBUG_TESTS environment variable is set
        if not os.environ.get(cls.DEBUG_TESTS, False):
            os.remove(cls.TEST_FILE_NAME)

    def test_default_sketch(self):
        sketch = Sketch("sketch.s")
        self.assertTrue(sketch.base.is_same((0, 0, 0)))
        self.assertTrue(sketch.u_vec.is_same((1, 0, 0)))
        self.assertTrue(sketch.v_vec.is_same((0, 1, 0)))
        self.assertEqual(0, len(sketch))
        self.assertEqual(0, len(sketch.vertices))

    def test_wdb_default_sketch(self):
        sketch = self.brl_db.lookup("sketch.s")
        self.assertTrue(sketch.base.is_same((0, 0, 0)))
        self.assertTrue(sketch.u_vec.is_same((1, 0, 0)))
        self.assertTrue(sketch.v_vec.is_same((0, 1, 0)))
        self.assertEqual(0, len(sketch))
        self.assertEqual(0, len(sketch.vertices))

    def test_example_sketch(self):
        sketch = Sketch.example_sketch()
        self.brl_db.save(sketch)
        result = self.brl_db.lookup(sketch.name)
        self.assertTrue(sketch.is_same(result))

if __name__ == "__main__":
    unittest.main()

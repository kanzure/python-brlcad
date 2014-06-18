import os
import unittest
from brlcad.primitives import bot
import brlcad.wdb as wdb


class BOTTestCase(unittest.TestCase):

    TEST_FILE_NAME = "test_bot.g"

    DEBUG_TESTS = "DEBUG_TESTS"

    @classmethod
    def setUpClass(cls):
        # create the test DB:
        if os.path.isfile(cls.TEST_FILE_NAME):
            os.remove(cls.TEST_FILE_NAME)
        with wdb.WDB(cls.TEST_FILE_NAME, "BRL-CAD geometry for testing sketch primitive") as brl_db:
            brl_db.bot("bot.s")
        # load the DB and cache it in a class variable:
        cls.brl_db = wdb.WDB(cls.TEST_FILE_NAME)

    @classmethod
    def tearDownClass(cls):
        # close the test DB
        cls.brl_db.close()
        # delete the test DB except the DEBUG_TESTS environment variable is set
        if not os.environ.get(cls.DEBUG_TESTS, False):
            os.remove(cls.TEST_FILE_NAME)

    def test_bot_solid(self):
        prism = bot.BOT_SOLID(name="prism.s")
        prism.add_face(bot.Face(bot=prism, vertices=[[0, 0, 1], [1, 0, 0], [0, 1, 0]]))
        prism.add_face(bot.Face(bot=prism, vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
        prism.add_face(bot.Face(bot=prism, vertices=[[0, 0, 1], [1, 0, 0], [0, 0, 0]]))

        self.brl_db.save(prism)
        result = self.brl_db.lookup(prism.name)
        self.assertTrue(prism.has_same_data(result))

    def test_bot_plates(self):
        parallel_triangles = bot.BOT_PLATES(name="sheets.s")
        parallel_triangles.add_face(bot.PlateFace(bot=parallel_triangles, vertices=[[0, 1, 1], [0, 1, 0], [0, 0, 1]],
                                                  thickness=1, face_mode=True))
        parallel_triangles.add_face(bot.PlateFace(bot=parallel_triangles, vertices=[[8, 1, 1], [8, 1, 0], [8, 0, 1]],
                                                  thickness=3, face_mode=False))
        parallel_triangles.add_face(bot.PlateFace(bot=parallel_triangles, vertices=[[13, 1, 1], [13, 1, 0], [13, 0, 1]],
                                                  thickness=2, face_mode=True))

        self.brl_db.save(parallel_triangles)
        result = self.brl_db.lookup(parallel_triangles.name)
        self.assertTrue(parallel_triangles.has_same_data(result))


if __name__ == "__main__":
    unittest.main()

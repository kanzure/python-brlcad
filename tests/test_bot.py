import os
import unittest
import math
from brlcad.primitives import bot
from brlcad.primitives.bot import PlateFace, Face

import brlcad.wdb as wdb


class SketchTestCase(unittest.TestCase):

    TEST_FILE_NAME = "test_bot.g"

    DEBUG_TESTS = "DEBUG_TESTS"

    @classmethod
    def setUpClass(cls):
        # create the test DB:
        if os.path.isfile(cls.TEST_FILE_NAME):
            os.remove(cls.TEST_FILE_NAME)
        with wdb.WDB(cls.TEST_FILE_NAME, "BRL-CAD geometry for testing sketch primitive") as brl_db:
            brl_db.sketch("bot.s")
        # load the DB and cache it in a class variable:
        cls.brl_db = wdb.WDB(cls.TEST_FILE_NAME)

    @classmethod
    def tearDownClass(cls):
        # close the test DB
        cls.brl_db.close()
        # delete the test DB except the DEBUG_TESTS environment variable is set
        if not os.environ.get(cls.DEBUG_TESTS, False):
            os.remove(cls.TEST_FILE_NAME)

    def test_example_sketch(self):
        bot_p = bot.BOT_PLATES(name="prism.s")
        bot_p.add_face(bot.PlateFace(bot=bot_p, vertices=[[0, 0, 1], [1, 0, 0], [0, 1, 0]], thickness=5, face_mode=True))
        bot_p.add_face(bot.PlateFace(bot=bot_p, vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]], thickness=1, face_mode=True))
        bot_p.add_face(bot.PlateFace(bot=bot_p, vertices=[[0, 0, 1], [0, 0, 0], [0, 1, 0]], thickness=1, face_mode=True))
        bot_p.add_face(bot.PlateFace(bot=bot_p, vertices=[[0, 0, 1], [1, 0, 0], [0, 0, 0]], thickness=1, face_mode=True))

        self.brl_db.save(bot_p)
        result = self.brl_db.lookup(bot_p.name)
        self.assertTrue(bot_p.has_same_data(result))

if __name__ == "__main__":
    unittest.main()

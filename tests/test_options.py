import unittest

import brlcad.install.options as options

class OptionsTestCase(unittest.TestCase):
    def test_is_win(self):
        self.assertTrue(options.is_win("windows"))

    def test_is_win_not(self):
        self.assertFalse(options.is_win("linux"))

if __name__ == "__main__":
    unittest.main()

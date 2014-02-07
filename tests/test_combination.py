import unittest

from brlcad.primitives.combination import union, intersect, subtract, negate, xor, LeafNode


class CombinationTestCase(unittest.TestCase):
    def test_union(self):
        self.assertEqual(
            "u[1, 2, 3, 4]",
            str(union("1", "2", "3", "4")),
        )

    def test_intersect(self):
        self.assertEqual(
            "n[1, 2, 3]",
            str(intersect("1", "2", LeafNode("3"))),
        )

    def test_subtract(self):
        self.assertEqual(
            "(1 - 2)",
            str(subtract("1", "2")),
        )

    def test_negate(self):
        self.assertEqual(
            "not(1)",
            str(negate("1")),
        )

    def test_xor(self):
        self.assertEqual(
            "^[1, 2, 3, 4]",
            str(xor("1", "2", "3", "4")),
        )

    def test_complex_condition(self):
        self.assertEqual(
            "u[3, 4, 1, 2, 5, 6, (not(7) - (8 - 9)), 10, 11, ^[15, 16, 12, 13, 14, n[19, 20, 21, 17, 18]]]",
            str(
                union(
                    "1", "2",
                    union("3", "4"),
                    union("5", "6"),
                    subtract(
                        negate("7"),
                        subtract("8", "9")
                    ),
                    union("10"),
                    "11",
                    xor(
                        "12", negate(negate("13")), "14",
                        xor("15", "16"),
                        intersect(
                            "17", "18",
                            intersect("19", "20", "21")
                        )
                    )
                )
            )
        )

if __name__ == "__main__":
    unittest.main()

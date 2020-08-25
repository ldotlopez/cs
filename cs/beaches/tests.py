import unittest
from os import path

from cs.beaches import parse

SAMPLE_DIR = path.dirname(path.realpath(__file__)) + "/samples"


def read_sample(x):
    with open(f"{SAMPLE_DIR}/{x}") as fh:
        return fh.read()


class BeachesTest(unittest.TestCase):
    def test_multislot_parse_all(self):
        x = parse(read_sample("multipleslots.html"))
        self.assertEqual(len(x), 16)


if __name__ == "__main__":
    unittest.main()

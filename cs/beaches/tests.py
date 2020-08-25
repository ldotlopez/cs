import unittest
from os import path
from unittest.mock import patch

from cs.beaches import parse

SAMPLE_DIR = path.dirname(path.realpath(__file__)) + "/samples"


def read_sample(x):
    with open(f"{SAMPLE_DIR}/{x}") as fh:
        return fh.read()


class FakeTest(unittest.TestCase):
    def test_multislot_parse_all(self):
        x = parse(read_sample("multipleslots.html"))
        self.assertEqual(len(x), 16)
    # def test_multislot_get_info_simplified(self):
    #     with patch('beaches._fetch', side_effect=read_sample('multipleslots.html'):
    #         beaches.get_info()


if __name__ == "__main__":
    unittest.main()

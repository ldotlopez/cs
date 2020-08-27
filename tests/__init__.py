import json
import unittest
from os import path

from cs import pharmacies

SAMPLES_DIR = path.dirname(path.realpath(__file__)) + "/samples"


def read_sample(x):
    with open(f"{SAMPLES_DIR}/{x}") as fh:
        return fh.read()

class PharmaciesTest(unittest.TestCase):
    def test_parse(self):
        data = pharmacies.parse(read_sample("pharma-8.50.json"))
        self.assertTrue(isinstance(data, list))
        self.assertTrue(all([isinstance(x, pharmacies.Item) for x in data]))
        self.assertEqual(len(data), 2)

    def test_item(self):
        d1 = json.loads(read_sample("pharma-8.50.json"))['data'][0]
        d1['direccion'] = 'foo n? 8'
        i = pharmacies.Item.from_origin(d1)
        self.assertEqual(i.address, "Foo Nº 8")

if __name__ == "__main__":
    unittest.main()

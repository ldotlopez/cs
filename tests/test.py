#!/usr/bin/env python3

import datetime
import os
import unittest
from unittest.mock import patch

import itv


def fetch(center_code, vehicle_class=itv.VehicleClass.LIGHT, date=None):
    samplename = date.strftime("%Y-%m-%d.html")
    return read_sample(samplename)


def read_sample(name):
    samplepath = os.path.dirname(__file__) + "/samples/" + name
    with open(samplepath, 'rb') as fh:
        return fh.read()


class ParserTest(unittest.TestCase):
    def test_simple_no_slots(self):
        data = itv.parse(read_sample("2020-06-01.html"))

        self.assertEqual(len(data), 7)
        self.assertEqual(list(data.values()), [False] * 7)

    def test_simple_no_slotsslots(self):
        data = itv.parse(read_sample("2020-06-08.html"))

        self.assertEqual(len(data), 7)
        self.assertTrue(True in list(data.values()))

    def test_no_agenda(self):
        with self.assertRaises(itv.NoData):
            itv.parse(read_sample("2020-06-22.html"))


class QueryTest(unittest.TestCase):
    def test_query(self):
        with patch('itv.fetch', side_effect=fetch) as mock_method:
            date = datetime.datetime(year=2020, month=6, day=1)
            req = itv.query("1201", date)


if __name__ == "__main__":
    unittest.main()

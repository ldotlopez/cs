#!/usr/bin/env python3

import datetime
import os
import unittest
from unittest.mock import patch

import itv


def fetch(center, vehicle_size, date=None):
    samplename = date.strftime("%Y-%m-%d.html")
    return read_sample(samplename)


def read_sample(name):
    samplepath = os.path.dirname(__file__) + "/samples/" + name
    with open(samplepath, 'rb') as fh:
        return fh.read()


def idx_data(data):
    return data[0:-1], data[-1]


class ParserTest(unittest.TestCase):
    def test_unavailable_slots(self):
        data = itv.parse(read_sample("2020-06-01.html"))
        data = dict(map(idx_data, data))
        self.assertFalse(any(data.values()))

    def test_available_slots(self):
        data = itv.parse(read_sample("2020-06-08.html"))
        data = dict(map(idx_data, data))
        self.assertTrue(any(data.values()))
        self.assertTrue(data[('06', '10', '18', '30')])

    def test_no_slots(self):
        with self.assertRaises(itv.NoSlots):
            itv.parse(read_sample("2020-06-22.html"))


class QueryTest(unittest.TestCase):
    def test_query(self):
        with patch('itv.fetch', side_effect=fetch) as mock_method:
            date = datetime.datetime(year=2020, month=6, day=1)
            req = itv.query("1201", date)


if __name__ == "__main__":
    unittest.main()

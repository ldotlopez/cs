#!/usr/bin/env python3

import datetime
import os
import unittest
from unittest.mock import patch

import itv


def fetch(center, vehicle_size, date):
    samplename = date.strftime("%Y-%m-%d.html")
    return read_sample(samplename)


def read_sample(name):
    samplepath = os.path.dirname(__file__) + "/samples/" + name
    with open(samplepath, "rb") as fh:
        return fh.read()


def idx_data(data):
    return data[0:-1], data[-1]


class UtilsMixin:
    def assertParsedValue(self, data, idx, value):
        idx = datetime.datetime(
            year=int(idx[0]),
            month=int(idx[1]),
            day=int(idx[2]),
            hour=int(idx[3]),
            minute=int(idx[4]),
        )
        self.assertEqual(dict(data)[idx], value)


class ParserTest(unittest.TestCase, UtilsMixin):
    def test_unavailable_slots(self):
        data = itv.parse(read_sample("2021-07-05.html"))
        data = dict(map(idx_data, data))
        self.assertFalse(any(data.values()))

    def test_available_slots(self):
        data = itv.parse(read_sample("2021-07-26.html"))
        self.assertParsedValue(data, [2021, 7, 30, 7, 15], False)
        self.assertParsedValue(data, [2021, 7, 30, 7, 45], True)
        self.assertParsedValue(data, [2021, 7, 30, 8, 00], False)

    def test_no_slots(self):
        with self.assertRaises(itv.NoSlots):
            itv.parse(read_sample("2021-08-30.html"))


class QueryTest(unittest.TestCase, UtilsMixin):
    def test_query_without_slots(self):
        with patch("itv.fetch", side_effect=fetch) as mock_method:
            date = datetime.datetime(year=2021, month=7, day=5)
            res = dict(itv.query(date=date))

            self.assertTrue(not all(res.values()))

    def test_query_with_slots(self):
        with patch("itv.fetch", side_effect=fetch) as mock_method:
            date = datetime.datetime(year=2021, month=7, day=26)
            res = dict(itv.query(date=date))

            self.assertTrue(any(res.values()))
            self.assertParsedValue(res, [2021, 7, 30, 7, 45], True)

    def test_query_with_slots_and_weeks_ahead(self):
        with patch("itv.fetch", side_effect=fetch) as mock_method:
            date = datetime.datetime(year=2021, month=7, day=19)
            res = dict(itv.query(date=date, weeks_ahead=2))

            self.assertTrue(any(res.values()))
            self.assertParsedValue(res, [2021, 7, 30, 7, 45], True)

    def test_query_with_slots_and_weeks_ahead_and_beyond(self):
        with patch("itv.fetch", side_effect=fetch) as mock_method:
            date = datetime.datetime(year=2021, month=7, day=5)
            res = itv.query(date=date, weeks_ahead=4)

            self.assertParsedValue(res, [2021, 7, 30, 7, 15], False)
            self.assertParsedValue(res, [2021, 7, 30, 7, 45], True)
            self.assertParsedValue(res, [2021, 7, 30, 8, 00], False)


    pass

if __name__ == "__main__":
    unittest.main()

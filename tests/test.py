#!/usr/bin/env python3

import os
import unittest

import itv


def fetch(sess, request):
    import ipdb; ipdb.set_trace(); pass
    with open(monday.strftime("%Y-%m-%d.html"),) as fh:
        return fh.read()


def read_sample(name):
    samplepath = os.path.dirname(__file__) + '/samples/' + name
    with open(samplepath, encoding='utf-8') as fh:
        return fh.read()


class ParserTest(unittest.TestCase):
    def test_simple_no_slots(self):
        data = itv.parse(read_sample('2020-06-01.html'))

        self.assertEqual(len(data), 7)
        self.assertEqual(list(data.values()), [False] * 7)

    def test_simple_slots(self):
        data = itv.parse(read_sample('2020-06-08.html'))

        self.assertEqual(len(data), 7)
        self.assertTrue(True in list(data.values()))

    def test_no_agenda(self):
        with self.assertRaises(itv.NoData):
            itv.parse(read_sample('2020-06-22.html'))


if __name__ == '__main__':
    unittest.main()

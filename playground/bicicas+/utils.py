#!/env/bin/python

import csv
import datetime
import enum
import functools
import sys


DELIMITER = ","
QUOTECHAR = "'"
STATE_FIELDS = [
    'id', 'name', 'lat', 'lng', 'available', 'capacity', 'percent',
    'ts', 'dt', 'weekday', 'hour', 'minute']


class RowFormatError(Exception):
    pass


class Weekday(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class State(object):
    def __init__(self, id, name, lat, lng, ts, available, capacity):
        self.id = id
        self.name = name
        self.lat = float(lat)
        self.lng = float(lng)
        self.ts = int(ts)
        self.available = int(available)
        self.capacity = int(capacity)

    @property
    @functools.lru_cache(maxsize=1)
    def percent(self):
        try:
            return self.available / self.capacity
        except ZeroDivisionError:
            return 0

    @property
    @functools.lru_cache(maxsize=1)
    def dt(self):
        return datetime.datetime.fromtimestamp(self.ts)

    @property
    @functools.lru_cache(maxsize=1)
    def weekday(self):
        return Weekday(self.dt.weekday()).name

    @property
    @functools.lru_cache(maxsize=1)
    def hour(self):
        return self.dt.hour

    @property
    @functools.lru_cache(maxsize=1)
    def minute(self):
        return self.dt.minute

    def as_record(self):
        return [getattr(self, x) for x in STATE_FIELDS]


def load_datafile(fh):
    reader = csv.reader(fh, delimiter=DELIMITER, quotechar=QUOTECHAR)
    yield from reader


def dump_datafile(fh, states):
    writer = csv.writer(fh, delimiter=DELIMITER, quotechar=QUOTECHAR,
                        quoting=csv.QUOTE_MINIMAL)

    writer.writerow(STATE_FIELDS)
    for row in states:
        writer.writerow(row.as_record())


def parse_row(row):
    try:
        (ts, id, name, lat, lng, available, capacity) = row
    except ValueError as e:
        raise RowFormatError() from e

    return State(
        id=id,
        name=name,
        lat=float(lat),
        lng=float(lng),
        ts=int(ts),
        available=int(available),
        capacity=int(capacity))


def convert(fhin, fhout):
    records = []
    for row in load_datafile(fhin):
        try:
            records.append(parse_row(row))
        except RowFormatError:
            pass

    dump_datafile(fhout, records)


with open(sys.argv[1]) as fhin:
    convert(fhin, sys.stdout)
#!/usr/bin/env python3

import csv
import json
import time
from os import path
from urllib import request


def fetch(url):
    with request.urlopen(url) as fh:
        buff = fh.read()

    return buff


def get_data(buff):
    return json.loads(buff)[0]


def now():
    return round(time.time())


def data_iter(data):
    for station in sorted(data['ocupacion'], key=lambda x: x['id']):
        yield [station[x] for x in
               ['id', 'punto', 'latitud', 'longitud', 'ocupados', 'puestos']]


def dump(timestamp, rows, path):
    with open(path, 'a') as fh:
        writer = csv.writer(fh, delimiter=',', quotechar="'",
                            quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow([timestamp] + row)


def main():
    URL = 'http://gestiona.bicicas.es/apps/apps.php'

    buff = fetch(URL).decode('utf-8')
    data = get_data(buff)
    rows = data_iter(data)
    timestamp = now()

    csvfile = path.dirname(path.realpath(__file__)) + "/data.csv"
    dump(timestamp, rows, csvfile)


if __name__ == '__main__':
    main()

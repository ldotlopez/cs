#!/usr/bin/env python3

import datetime
import random
import time
import urllib

import bs4
import requests


class NoData(Exception):
    pass


class ParseError(Exception):
    pass


class InvalidResponse(Exception):
    pass


def parse(buff):
    def get_day(slot):
        return next(slot.parent.children)

    soup = bs4.BeautifulSoup(buff, features="html5lib")
    slots = soup.select("td")
    if not slots:
        raise NoData()

    results = {}
    day = None

    for slot in slots:
        if slot.text:
            day = slot.text
            results[day] = False
        else:
            classes = slot.attrs.get("class")
            if "pasado" not in classes and "ocupado" not in classes:
                results[day] = True

    if len(results) != 7:
        raise ParseError()

    return results


def fetch(sess, date=None, mock=False):
    if date is None:
        date = datetime.datetime.now()

    monday = date - datetime.timedelta(days=date.weekday())

    if mock is True:
        with open(monday.strftime("%Y-%m-%d.html"),) as fh:
            return fh.read()

    req = requests.Request(
        url="http://www.itvcvr.com/citaprevia/index.php",
        method="POST",
        data=urllib.parse.urlencode(
            dict(
                ajax="cargarDatosTablaFechas",
                fecha=monday.strftime("%Y-%m-%d"),
                centro="1201",
                tipoVehiculo="Ligeros",
            )
        ),
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0)"
                "Gecko/20100101 Firefox/76.0"
            ),
            "Accept": "*/*",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://www.itvcvr.com",
            "Connection": "close",
            "Referer": "http://www.itvcvr.com/citaprevia/index.php",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        },
    )

    resp = sess.send(req.prepare())
    if resp.status_code != 200:
        raise InvalidResponse(resp)

    resp.close()
    return resp.text


def main():
    sess = requests.Session()

    found = False
    weeks_ahead = 0

    while True:
        if weeks_ahead >= 10:
            print("😿 Sin fechas")
            break

        date = datetime.datetime.now() + datetime.timedelta(
            days=7 * weeks_ahead
        )

        # Fetch data or die
        try:
            buff = fetch(sess, date, mock=False)
        except InvalidResponse:
            print("🙀 Error al cargar datos")
            break

        # Parse data (die if no slots found)
        try:
            data = parse(buff)
        except NoData:
            print("😿 Sin fechas")
            break

        available_dates = [d for (d, available) in data.items() if available]
        if available_dates:
            for d in available_dates:
                print(f"😺 Fecha libre: {d}")

            break

        weeks_ahead += 1


def test_parse():
    import sys

    with open(sys.argv[1]) as fh:
        data = parse(fh.read())
        import ipdb

        ipdb.set_trace()
        pass


if __name__ == "__main__":
    main()
    # fetch(requests.Session())

#!/usr/bin/env python3

import datetime
import enum
import random
import re
import time
import urllib

import bs4

_ORIGIN = "http://www.itvcvr.com"
_QUERY_URL = "http://www.itvcvr.com/citaprevia/index.php"
_UA = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0)"
    "Gecko/20100101 Firefox/76.0"
)
_DEFAULT_HEADERS = {
    "User-Agent": _UA,
    "Accept": "*/*",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": _ORIGIN,
    "Connection": "close",
    "Referer": _QUERY_URL,
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


class VehicleClass(enum.Enum):
    LIGHT = "Ligeros"


class NoData(Exception):
    pass


class ParseError(Exception):
    pass


class InvalidResponse(Exception):
    pass


def parse_(buff):
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


def parse(buff):
    soup = bs4.BeautifulSoup(buff, features="html5lib")

    # Parse slots in agenda
    # in_day_slots = [
    #     ('07', '00'),
    #     ('07', '15'),
    #     ('07', '30'),
    #     ('07', '45'),
    #     ....
    in_day_slots = soup.select("table#tablaDocs th b")
    in_day_slots = [x.text for x in in_day_slots]
    in_day_slots = [re.search(r"(\d+)(\d{2})", x) for x in in_day_slots]
    in_day_slots = [m.groups() for m in in_day_slots if m]

    slots = soup.select("td")
    if not slots:
        raise NoData()

    ret = []
    for row in soup.select("table#tablaDocs tr"):
        day_cell = row.select_one("td")
        if not day_cell:
            continue

        m = re.search(r"(\d+)/(\d+)", day_cell.text)
        if not m:
            continue

        curr_day, curr_month = m.groups()

        for (idx, cell) in enumerate(list(row.select("td"))[1:]):
            cell_classes = cell.attrs.get("class") or []
            available = (
                "pasado" not in cell_classes and "ocupado" not in cell_classes
            )
            ret.append(
                (curr_month, curr_day) + in_day_slots[idx] + (available,)
            )

    return ret


def _get_monday(base=None, weeks_ahead=0):
    if base is None:
        base = datetime.datetime.now()
    base = base - datetime.timedelta(days=base.weekday())

    return base + datetime.timedelta(days=7 * weeks_ahead)


def query(center_code, vehicle_class=VehicleClass.LIGHT, date=None):
    date = _get_monday(date)
    buff = fetch(
        center_code=center_code, vehicle_class=vehicle_class, date=date
    ).decode("utf-8")

    data = parse(buff)
    data = [
        (
            datetime.datetime(
                year=date.year,
                month=int(x[0]),
                day=int(x[1]),
                hour=int(x[2]),
                minute=int(x[3]),
            ),
            x[4],
        )
        for x in data
    ]

    return data


def fetch(center_code, vehicle_class=VehicleClass.LIGHT, date=None):
    payload = dict(
        ajax="cargarDatosTablaFechas",
        fecha=date.strftime("%Y-%m-%d"),
        centro=center_code,
        tipoVehiculo=vehicle_class.value,
    )
    payload = urllib.parse.urlencode(payload)
    req = urllib.request.Request(
        _QUERY_URL, method="POST", data=payload, headers=_DEFAULT_HEADERS
    )
    resp = urllib.request.urlopen(req)
    if resp.status != 200:
        raise InvalidResponse(resp)

    return resp.read()


def main():
    sess = requests.Session()

    found = False
    weeks_ahead = 0

    # Initial date is past monday (or today if it's monday)
    basedate = datetime.datetime.now()
    basedate = basedate - datetime.timedelta(days=basedate.weekday())

    while True:
        if weeks_ahead >= 10:
            print("😿 Sin fechas")
            break

        date = basedate + datetime.timedelta(days=7 * weeks_ahead)

        # Fetch data or die
        try:
            buff = fetch(sess, "1201", date=date)
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

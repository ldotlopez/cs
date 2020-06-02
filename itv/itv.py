#!/usr/bin/env python3

import datetime
import enum
import itertools
import json
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


class Center(enum.Enum):
    CASTELLO = "1201"
    VILA_REAL = "1202"
    VINAROS = "1203"
    PORT_SAGUNT = "4612"

    @classmethod
    def from_arg(cls, arg):
        m = {
            "castello": cls.CASTELLO,
            "vila-real": cls.VILA_REAL,
            "vinaros": cls.VINAROS,
            "port-sagunt": cls.PORT_SAGUNT,
        }
        if arg in m:
            return m[arg]
        else:
            raise ValueError(arg)


class VehicleSize(enum.Enum):
    LIGHT = "Ligeros"
    HEAVY = "Pesados"

    @classmethod
    def from_arg(cls, arg):
        m = {"light": cls.LIGHT, "heavy": cls.HEAVY}
        if arg in m:
            return m[arg]
        else:
            raise ValueError(arg)


def fetch(center, vehicle_size, date):
    payload = dict(
        ajax="cargarDatosTablaFechas",
        fecha=date.strftime("%Y-%m-%d"),
        centro=center.value,
        tipoVehiculo=vehicle_size.value,
    )
    payload = urllib.parse.urlencode(payload).encode("utf-8")

    req = urllib.request.Request(
        _QUERY_URL, method="POST", data=payload, headers=_DEFAULT_HEADERS
    )

    resp = urllib.request.urlopen(req)
    if resp.status != 200:
        raise InvalidResponse(resp)

    return resp.read()


def parse(buff, year=None):
    if year is None:
        year = datetime.datetime.now().year

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
        raise NoSlots()

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

    ret = [
        (
            datetime.datetime(
                year=year,
                month=int(x[0]),
                day=int(x[1]),
                hour=int(x[2]),
                minute=int(x[3]),
            ),
            x[4],
        )
        for x in ret
    ]

    return ret


def _query(center, vehicle_size, date):
    buff = fetch(center=center, vehicle_size=vehicle_size, date=date)
    buff = buff.decode("utf-8")
    res = parse(buff, year=date.year)

    return res


def query(
    center=Center.CASTELLO,
    vehicle_size=VehicleSize.LIGHT,
    date=None,
    weeks_ahead=1,
    quick=False,
):
    if date is None:
        date = datetime.datetime.now()

    ret = []
    for week in range(weeks_ahead):
        try:
            part = _query(
                center=center,
                vehicle_size=vehicle_size,
                date=date + datetime.timedelta(days=7 * week),
            )

        except NoSlots:
            break

        if quick:
            available = [x for x in part if x[1]]
            if available:
                return [available[0]]

        ret.extend(part)

    return ret


def _show_for_machines(data):
    import ipdb; ipdb.set_trace(); pass
    data = [str(dt) for dt in data]
    print(json.dumps(data))
    return


def _show_for_humans(data):
    if data:
        for dt in (x[0] for x in data if x[1]):
            dtstr = dt.strftime("%d/%m/%Y (%H:%M)")
            print(f"😺 Free slot: {dtstr}")

    else:
        print("😿 No available slots")


class NoSlots(Exception):
    pass


class ParseError(Exception):
    pass


class InvalidResponse(Exception):
    pass


def main(argv):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        action="store_true",
        help="Dump available slots in JSON format",
    )
    parser.add_argument(
        "--quick", action="store_true", help="Just print first available slot"
    )
    parser.add_argument(
        "--weeks",
        dest="weeks_ahead",
        type=int,
        default=1,
        help="How many weeks ahead to check",
    )

    parser.add_argument(
        "--center",
        choices=["castello", "port-sagunt", "vila-real", "vinaros"],
        default="castello",
        help="ITV center",
    )
    parser.add_argument(
        "--vehicle",
        dest="vehicle_size",
        choices=["light", "heavy"],
        default="light",
        help="Vehicle type",
    )
    args = parser.parse_args(argv)
    args.center = Center.from_arg(args.center)
    args.vehicle_size = VehicleSize.from_arg(args.vehicle_size)

    res = query(
        center=args.center,
        vehicle_size=args.vehicle_size,
        weeks_ahead=args.weeks_ahead,
        quick=args.quick,
    )

    if args.json:
        _show_for_machines(res)
    else:
        _show_for_humans(res)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])

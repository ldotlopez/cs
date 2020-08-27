#!/usr/bin/python3

import dataclasses
import datetime
import json
import re
import urllib.parse
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) "
    "Gecko/20100101 Firefox/61.0"
)


@dataclasses.dataclass
class Item:
    """
    {
        "id": "38",
        "direccion": "Plaza SIERRA DE GREDOS, N? 2",
        "horario": "12/04/2020 De 9 ma\u00f1ana a 22:00 h.",
        "poblacion": "Castell\u00f3n",
        "farmacia": "FARMACIA J.M. SALAZAR C.B.",
        "telefono": "964212275",
        "latitud": -0.0523122102022171,
        "horarioFin": "",
        "longitud": 39.97365188598633,
        "codpostal": "12006"
    },
    """

    address: str
    lat: int
    lng: int
    name: str
    phone: str
    schedule: str
    notes: list
    _updated: int

    @classmethod
    def from_origin(cls, x):
        def fix_address(addr):
            return re.sub(r"n\?\s+(\d+)", r"nº \1", addr, flags=re.IGNORECASE)

        def camelcase(s):
            return " ".join([x.capitalize() for x in s.split(" ")])

        def build_notes(d):
            notes = []

            end = d.get("horarioFin")
            if end:
                notes.append(end)

            return notes

        return cls(
            address=camelcase(fix_address(x["direccion"])),
            lat=x["latitud"],
            lng=x["longitud"],
            schedule=x["horario"].capitalize(),
            name=camelcase(x["farmacia"]),
            phone=x["telefono"],
            notes=build_notes(x),
            _updated=x.get("_updated") or datetime.datetime.now(),
        )

    def asdict(self):
        d = dataclasses.asdict(self)
        d["_updated"] = self._updated.timestamp()
        return d


def get_pharmacies(now=None, city="0402"):
    return parse(_fetch(now=now, city=city))


def parse(buff):
    data = json.loads(buff)["data"]
    return [Item.from_origin(x) for x in data]


def _fetch(now=None, city="0402"):
    if now is None:
        now = datetime.datetime.now()

    payload = urllib.parse.urlencode(
        dict(
            fecha="{now.day:02d}/{now.month:02d}/{now.year}".format(now=now),
            pob=str(city),
            p_clave="",
            gua="1",
        )
    ).encode("utf-8")

    req = urllib.request.Request(
        "http://www.cofcastellon.org/Farmacias",
        data=payload,
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req) as fh:
        return fh.read().decode("iso-8859-15")

#!/usr/bin/python3

import datetime
import json
import urllib.parse
import urllib.request


def get_pharmacies(now=None, city="0402"):
    """
    [
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
        ...
    ]
    """

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

    handle = urllib.request.urlopen(
        "http://www.cofcastellon.org/Farmacias", data=payload
    )
    resp = handle.read().decode("iso-8859-15")
    resp = json.loads(resp)
    resp = resp["data"]

    if now.hour == 21 and now.minute >= 30:
        resp.extend(
            get_pharmacies(now + datetime.timedelta(days=1), city=city)
        )

    return [normalize(x) for x in resp]


def normalize(x):
    return dict(
        address=x["direccion"],
        lat=x["latitud"],
        lng=x["longitud"],
        schedule=x["horario"],
        name=x["farmacia"],
        phone=x["telefono"],
    )

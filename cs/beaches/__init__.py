import datetime
import sys
from urllib import request

import bs4

BEACH_INFO_URL_TMPL = (
    "https://medigrupgestion.com/playas/info-banderas?id={id}"
)

BEACHES = [
    "https://medigrupgestion.com/playas/info-banderas?id=52",
    "https://medigrupgestion.com/playas/info-banderas?id=53",
    "https://medigrupgestion.com/playas/info-banderas?id=54",
]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) "
    "Gecko/20100101 Firefox/61.0"
)

GEO = {
    "Playa el Pinar (Torre 1)": (39.9798951, 0.0219168),
    "Playa el Pinar (Torre 2)": (39.9828111, 0.0230373),
    "Playa el Pinar (Torre 3)": (39.9859331, 0.0238203),
    "Playa el Pinar (Torre 4)": (39.990664, 0.027420),
    "Playa Gurugú (Torre 5)": (39.9963799, 0.0293831),
    "Playa Serradal (Torre 6)": (40.0055111, 0.0304678),
    "Playa Serradal (Torre 7)": (40.009187, 0.034000),
}


def parse(buff):
    def add_timestamp(x, ts):
        x["_updated"] = ts
        return x

    now = datetime.datetime.now()
    soup = bs4.BeautifulSoup(buff, features="html5lib")
    beach = soup.select_one(".nombre-playa").text.strip()

    time_blocks = [
        x
        for x in soup.select(".container-azulado")
        if x.select_one(".titulo").text.startswith("Hora:")
    ]

    ret = []
    for block in time_blocks:
        t0 = datetime.datetime.strptime(
            block.select_one(".titulo").text[6:], "%H:%M"
        )
        updated = datetime.datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=t0.hour,
            minute=t0.minute,
        ).timestamp()

        for tower in block.select(".torre_datos"):
            tower_data = parse_tower(tower)
            tower_data["name"] = "%s (%s)" % (beach, tower_data.pop("name"))
            try:
                latlng = GEO[tower_data["name"]]
                tower_data["lat"] = latlng[1]
                tower_data["lng"] = latlng[0]
            except KeyError:
                print("W: no geo for f{tower_data.name}", file=sys.stderr)
                tower_data["lat"] = None
                tower_data["lng"] = None

            tower_data["_updated"] = updated
            ret.append(tower_data)

    return ret


def parse_tower(tower):
    t = [("roja", "danger"), ("amarilla", "warning"), ("verde", "ok")]

    name = tower.select_one(".torre_nombre").text.strip()
    classes = tower.select_one(".fondo-bandera i").attrs.get("class", [])
    state = "unknown"
    for (needle, state2) in t:
        if needle in classes:
            state = state2
            break

    return {"name": name, "state": state}


def get_info(prev=None):
    if prev is None:
        prev = []

    curr = []
    for url in BEACHES:
        curr.extend(parse(_fetch(url)))

    tmp = {}
    for x in prev + curr:
        if x["name"] not in tmp or x["_updated"] > tmp[x["name"]]["_updated"]:
            tmp[x["name"]] = x

    return list(tmp.values())


def _fetch(url):
    req = request.Request(url, headers={"User-Agent": UA})
    with request.urlopen(req) as fh:
        return fh.read()

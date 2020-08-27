import datetime
import sys
from urllib import request

import bs4

BEACH_INFO_URL_TMPL = (
    "https://medigrupgestion.com/playas/info-banderas?id={id}"
)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) "
    "Gecko/20100101 Firefox/61.0"
)


def latlng_for_name(name):
    # Those coors are from google maps, they are in (lnt, lat form), reversed
    # from expected
    geodata = {
        "Playa el Pinar (Torre 1)": (39.98079291981047,0.024510398622323848),
        "Playa el Pinar (Torre 2)": (39.9834547415974,0.02541826554436355),
        "Playa el Pinar (Torre 3)": (39.9868120639394,0.026553099196893193),
        "Playa el Pinar (Torre 4)": (39.98970550870041,0.02730965496524629),
        "Playa Gurugú (Torre 5)": (39.99814455843709, 0.029516773481117475),
        "Playa Serradal (Torre 6)": (40.005393021582826, 0.03265219929561969),
        "Playa Serradal (Torre 7)": (40.00934147350583, 0.03411735154554396),
    }

    latlng = geodata[name]
    return (latlng[1], latlng[0])


def parse(buff):
    def add_timestamp(x, ts):
        x["_updated"] = ts
        return x

    now = datetime.datetime.now()
    soup = bs4.BeautifulSoup(buff, features="html5lib")
    beach = soup.select_one(".nombre-playa").text.strip()

    ret = []

    curr_date = None
    for block in soup.select(".container-azulado .col-lg-12"):
        title = block.select_one(".titulo")
        if title and title.text.startswith("Hora:"):
            t0str = title.text[6:]
            t0 = datetime.datetime.strptime(t0str, "%H:%M")

            curr_date = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=t0.hour,
                minute=t0.minute,
            )
            curr_date = curr_date.timestamp()

        elif block.select_one(".torre_datos"):
            tower_data = parse_tower_element(block)
            tower_data["name"] = "%s (%s)" % (beach, tower_data.pop("name"))

            try:
                latlng = latlng_for_name(tower_data["name"])
                tower_data["lat"] = latlng[0]
                tower_data["lng"] = latlng[1]
            except KeyError:
                print("W: no geo for f{tower_data.name}", file=sys.stderr)
                tower_data["lat"] = None
                tower_data["lng"] = None

            tower_data["_updated"] = curr_date
            ret.append(tower_data)

    return ret


def parse_tower_element(tower):
    t = [("roja", "danger"), ("amarilla", "warning"), ("verde", "ok")]

    name = tower.select_one(".torre_nombre").text.strip()
    classes = tower.select_one(".fondo-bandera i").attrs.get("class", [])
    state = "unknown"
    for (needle, state2) in t:
        if needle in classes:
            state = state2
            break

    return {"name": name, "state": state}


def get_info(id):
    url = BEACH_INFO_URL_TMPL.format(id=id)
    req = request.Request(url, headers={"User-Agent": UA})
    with request.urlopen(req) as fh:
        return parse(fh.read())


def merge(infos):
    tmp = {}

    for x in infos:
        if x["name"] not in tmp or x["_updated"] >= tmp[x["name"]]["_updated"]:
            tmp[x["name"]] = x

    return list(tmp.values())

#!/usr/bin/python3

import argparse
import datetime
import json
import logging
import sys
import urllib.error

from cs import pharmacies

LOGGER = logging.getLogger("cs.pharmacies")


def _pharma_get(*args, **kwargs):
    try:
        return pharmacies.get_pharmacies(*args, **kwargs)
    except urllib.error.URLError as e:
        logmsg = f"Network error: {e!r}"
        LOGGER.error(logmsg)
        sys.exit(1)
    except json.decoder.JSONDecodeError as e:
        logmsg = f"Invalid JSON response '{e.doc[:15]}'"
        LOGGER.error(logmsg)
        sys.exit(1)


def main():
    logging.basicConfig()
    LOGGER.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--city-code", required=True)
    parser.add_argument("--output-file", required=False)
    parser.add_argument("--force-empty-output-file", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    data = _pharma_get()

    now = datetime.datetime.now()
    if now.hour == 21 and now.minute >= 30:
        data.extend(_pharma_get(now=now + datetime.timedelta(days=1)))

    data = {
        "_updated": now.timestamp(),
        "pharmacies": [x.asdict() for x in data],
    }
    jsondata = json.dumps(data, indent=2)

    if args.output_file:
        if data and not args.force_empty_output_file:
            with open(args.output_file, "w+", encoding="utf-8") as fh:
                fh.write(jsondata)
        else:
            logmsg = "Refusing to save empty data"
            LOGGER.error(logmsg)

    if args.verbose:
        print(jsondata)


if __name__ == "__main__":
    main()

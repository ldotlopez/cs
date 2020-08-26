import argparse
import functools
import itertools
import json
import logging
import sys
import time

from cs import beaches


def main():
    logging.basicConfig()
    beaches.LOGGER.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--data-file", required=False)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(sys.argv[1:])

    prev = []
    if args.data_file:
        try:
            with open(args.data_file, encoding="utf-8") as fh:
                prev = json.loads(fh.read())["beaches"]
        except (IOError, FileNotFoundError, ValueError, KeyError, TypeError):
            pass

    beach_data = list(
        itertools.chain.from_iterable(
            [beaches.get_info(id) for id in ["52", "53", "54"]]
        )
    )
    beach_data = beaches.merge(prev + beach_data)

    info = {
        "_updated": int(time.mktime(time.localtime())),
        "beaches": beach_data,
    }

    if args.data_file:
        with open(args.data_file, "w+", encoding="utf-8") as fh:
            buff = json.dumps(info)
            fh.write(buff)

    if args.verbose:
        print(json.dumps(info))


if __name__ == "__main__":
    main()

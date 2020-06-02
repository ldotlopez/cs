#!/usr/bin/env python3

import datetime
import functools
import json
import random
import time


import itv


@functools.lru_cache(maxsize=8)
def _dump_enum(x):
    return x.name.lower().replace("_", "-")


@functools.lru_cache(maxsize=1024)
def _dump_datetime(x):
    return x.isoformat()


def main(argv):
    import argparse
    import sys

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--weeks",
        dest="weeks_ahead",
        type=int,
        default=4,
        help="How many weeks ahead to check",
    )

    parser.add_argument(
        "--center",
        choices=["castello", "port-sagunt", "vila-real", "vinaros", "all"],
        default="all",
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
    if args.center == "all":
        args.center = [x for x in itv.Center]
    else:
        args.center = [itv.Center.from_arg(args.center)]

    args.vehicle_size = itv.VehicleSize.from_arg(args.vehicle_size)

    data = []
    for center in args.center:
        center_data = []
        for week in range(args.weeks_ahead):
            dt = datetime.datetime.now() + datetime.timedelta(days=7 * week)
            try:
                print(
                    f"query {center} {args.vehicle_size} {dt}", file=sys.stderr
                )
                part = itv.query(
                    center=center, vehicle_size=args.vehicle_size, date=dt,
                )
            except (itv.ParseError, itv.InvalidResponse):
                break

            except itv.NoSlots:
                break

            time.sleep(5 + random.randint(-2, 2))
            center_data.extend(part)

        data.extend(
            [center, args.vehicle_size, x[0], x[1]] for x in center_data
        )

    print(
        json.dumps(
            [
                dict(
                    center=_dump_enum(x[0]),
                    vehicle_size=_dump_enum(x[1]),
                    date=_dump_datetime(x[2]),
                    available=x[3],
                )
                for x in data
            ]
        )
    )


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])

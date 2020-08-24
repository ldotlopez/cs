import argparse
import sys
import json

from cs import beaches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-file", required=False)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(sys.argv[1:])

    prev = []
    if args.data_file:
        try:
            with open(args.data_file, encoding="utf-8") as fh:
                prev = json.loads(fh.read())
        except (IOError, FileNotFoundError):
            pass

    info = beaches.get_info(prev)

    if args.data_file:
        with open(args.data_file, "w+", encoding="utf-8") as fh:
            buff = json.dumps(info)
            fh.write(buff)

    if args.verbose:
        print(json.dumps(info))


if __name__ == "__main__":
    main()

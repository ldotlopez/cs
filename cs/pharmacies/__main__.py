#!/usr/bin/python3

import json

from cs import pharmacies

if __name__ == "__main__":
    print(json.dumps(pharmacies.get_pharmacies(), indent=2))

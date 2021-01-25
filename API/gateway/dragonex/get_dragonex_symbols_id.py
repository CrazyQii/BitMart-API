from os import sys, path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import os
import requests
import json
from Gateway.base_url import dragonex_base_url


def get_symbols_id():
    symbols_id = {}
    response = requests.get(dragonex_base_url + "symbol/all")
    for i in response.json()["data"]:
        symbol_id = {}
        symbol_id[i["symbol"]] = i["symbol_id"]
        symbols_id.update(symbol_id)
    return symbols_id

def dump_json():
    try:
        is_file = os.path.isfile("dragonex_symbols_id.json")
        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "dragonex_symbols_id.json")
        with open(path, "w+") as f:
            symbols_details = json.dumps(get_symbols_id(), indent = 4)
            f.write(symbols_details)
        f.close()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    dump_json()

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import os
import requests
import json
import time
from constant.base_url import hotbit_base_url
import math


def get_symbol_details(url):
    symbols_details = {}
    response = requests.get(url)
    for i in response.json()["result"]:
        symbol = {}
        symbol["price_max_precision"] = i["money_prec"]
        symbol["quote_increment"] = pow(10, -i["money_prec"])
        symbols_details[i["stock"]+ "_" + i["money"]] = symbol
    return symbols_details

def dump_json():
    try:
        is_file = os.path.isfile("hotbit_symbols_details.json")
        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "hotbit_symbols_details.json")
        with open(path, "w+") as f:
            symbols_details = json.dumps(get_symbol_details(hotbit_base_url + "market.list"), indent = 4)
            f.write(symbols_details)
        f.close()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    dump_json()

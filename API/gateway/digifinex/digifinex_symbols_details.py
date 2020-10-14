from os import sys, path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import os
import requests
import json
import time
import math

base_url = "http://openapi.digifinex.vip/v3/markets"


def get_symbol_details(url):
    symbols_details = {}
    response = requests.get(url)
    print(response.json())
    for i in response.json()["data"]:
        symbol = {}
        symbol["price_max_precision"] = i["price_precision"]
        symbol["quote_increment"] = pow(10, -i["price_precision"])
        symbol['amount_precision'] = i['volume_precision']
        symbols_details[i['market'].upper()] = symbol
    return symbols_details

def dump_json():
    try:
        is_file = os.path.isfile("digifinex_symbols_details.json")
        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "digifinex_symbols_details.json")
        with open(path, "w+") as f:
            symbols_details = json.dumps(get_symbol_details(base_url), indent = 4)
            f.write(symbols_details)
        f.close()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    dump_json()

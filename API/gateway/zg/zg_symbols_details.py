from os import sys, path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import os
import requests
import json
import time
import math

base_url = "https://api.zg.com/openapi/v1/brokerInfo"

def symbol_convert(symbol):
        return '_'.join(symbol.split('USDT')) + "USDT"

def get_symbol_details(url):
    symbols_details = {}
    response = requests.get(url)
    print(response.json())
    if "symbols" in response.json().keys():
        for symbol_info in response.json()["symbols"]:
            symbol = {}
            symbol["price_max_precision"] = len(symbol_info["quotePrecision"]) -2
            symbol["quote_increment"] = float(symbol_info["quotePrecision"])
            symbol['amount_precision'] = float(symbol_info["baseAssetPrecision"])
            symbols_details[symbol_convert(symbol_info['symbol']).upper()] = symbol   
    return symbols_details

def dump_json():
    try:
        is_file = os.path.isfile("zg_symbols_details.json")
        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "zg_symbols_details.json")
        with open(path, "w+") as f:
            symbols_details = json.dumps(get_symbol_details(base_url), indent = 4)
            f.write(symbols_details)
        f.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    dump_json()

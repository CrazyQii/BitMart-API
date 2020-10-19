from os import sys, path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import os
import requests
import json

dev_url = "http://api-cloud.bitmart.com/"

def get_symbol_details(url):
    symbols_details = {}
    response = requests.get(url)
    for i in response.json()["data"]["symbols"]:
        symbol = {}
        symbol["price_max_precision"] = i["price_max_precision"]
        symbol["quote_increment"] = pow(10, -i["price_max_precision"])
        symbol["base_min_size"] = float(i["base_min_size"])
        symbols_details[i["symbol"]] = symbol
    return symbols_details

def dump_json():
    try:
        is_file = os.path.isfile("bitmart_symbols_details.json")
        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "bitmart_symbols_details.json")
        with open(path, "w+") as f:
            symbols_details = json.dumps(get_symbol_details(dev_url + "spot/v1/symbols/details"), indent = 4)
            f.write(symbols_details)
        f.close()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    dump_json()

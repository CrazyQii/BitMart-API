import re
import requests
import time
import os
import json

class DragonexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            return symbol.lower()
        except Exception as e:
            print(e)

    def load_symbols_id(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_id = {}
            with open(current_path + "/dragonex_symbols_id.json", "r") as f:
                symbols_id = json.load(f)
            f.close()
            return symbols_id
        except Exception as e:
            print(e)

    def get_symbol_id(self, symbol):
        try:
            symbols_id = self.load_symbols_id()
            return symbols_id[symbol]
        except Exception as e:
            print (e)


    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            symbol_id = self.get_symbol_id(symbol)
            url = self.urlbase + "market/real/?symbol_id=%s" % (symbol_id)
            response = requests.get(url)
            # print(response.content)
            return float(response.json()["data"][0]["close_price"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    Dragonex_public = DragonexPublic("https://openapi.dragonex.io/api/v1/")
    # print Dragonex_public.get_price("ODE_USDT")

import re
import requests
import time
import os
import json

class KucoinPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "-" + symbol_quote
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "api/v1/market/orderbook/level1?symbol=%s" % (symbol)
            response = requests.get(url)
            # print(response.content)
            return float(response.json()["data"]["price"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    kucoin_public = KucoinPublic("https://api.kucoin.com/")
    # print kucoin_public.get_price("ODE_ETH")

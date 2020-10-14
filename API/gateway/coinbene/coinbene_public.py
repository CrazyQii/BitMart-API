import requests
import json
import hashlib
import time
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Content-Type": "application/json;charset=utf-8", "Connection": "keep-alive"}
    
class CoinbenePublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase
        
    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def get_ticker(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/ticker?symbol=%s" % symbol
            response = requests.get(url)
            return response.json()["ticker"][0]
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/ticker?symbol=%s" % symbol
            response = requests.get(url)
            return float(response.json()["ticker"][0]["last"])
        except Exception as e:
            print(e)
            return None

    def get_precision(self, symbol):
        try:
            # symbol = self.symbol_convert(symbol)
            # url = self.urlbase + "market/symbol"
            # response = requests.get(url)
            # return response.json()
            if symbol == "EBC_ETH":
                return 8
            if symbol == "APL_ETH":
                return 8
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/market/orderbook?symbol=%s" % symbol
            response = requests.get(url)
            return response.json()["orderbook"]
        except Exception as e:
            print(e)

    def get_trades(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/trades?symbol=%s" % symbol
            response = requests.get(url)
            # print(response.content)
            return response.json()["trades"][0]
        except Exception as e:
            print(e)

if __name__ == "__main__":
    coinbene_public = CoinbenePublic()
    print (coinbene_public.get_orderbook("EBC_ETH")["asks"])

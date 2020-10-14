from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import requests
import re
from constant.base_url import coinis_base_url

class CoinisPublic(object):
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

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "sise/ticker?itemcode=%s" % symbol
            response = requests.get(url)
            return float(response.json()["data"]["OpenPrice"])
        except Exception as e:
            print(e)

    def get_ticker(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "sise/ticker?itemcode=%s" % symbol
            response = requests.get(url)
            # print(response.content)
            return response.json()["data"]
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "sise/orderbook?itemcode=%s" % symbol
            response = requests.get(url)
            # print(response.content)
            return response.json()["data"]
        except Exception as e:
            print(e)

if __name__ == "__main__":
    coinis = CoinisPublic(coinis_base_url)
    # print coinis.get_ticker("EBC_KRW")

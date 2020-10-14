from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import requests
import time
import re

class BitbayPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase + "Public/"

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def get_last_trade(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "%s/trades.json" % symbol
            response = requests.get(url)
            # print response.content
            return response.json()[-1]
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "%s/ticker.json" % symbol
            response = requests.get(url)
            # print response.content
            return float(response.json()["last"])
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "%s/orderbook.json" % symbol
            response = json.loads(requests.get(url).content)
            buy_orders = []
            sell_orders = []
            buy_total, sell_total = 0, 0
            for order in response["bids"]:
                buy_total += order[1]
                buy_orders.append({"count": 1,
                                   "amount": order[1],
                                   "total": buy_total,
                                   "price": order[0]})
            for order in response["asks"]:
                sell_total += order[1]
                sell_orders.append({"count": 1,
                                   "amount": order[1],
                                   "total": sell_total,
                                   "price": order[0]})
            return {"buys": buy_orders, "sells": sell_orders}
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            if symbol == "BOB_BTC":
                return 1e-8
        except Exception as e:
            print(e)

    def get_precision(self, symbol):
        try:
            if symbol == "BOB_BTC":
                return 8
        except Exception as e:
            print(e)


if __name__ == "__main__":
    bitbay = BitbayPublic("https://bitbay.net/API/")
    print bitbay.get_orderbook("BOB_BTC")
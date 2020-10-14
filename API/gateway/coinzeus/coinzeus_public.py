import requests
import json
import time
import re
import os

class CoinzeusPublic(object):

    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "/" + symbol_quote
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "ticker/orderBook"
            data = {"pairName": symbol}
            response = requests.post(url, data=data)
            orderbook = {}
            orderbook["sells"] = response.json()["data"]["sellList"]
            orderbook["buys"] = response.json()["data"]["buyList"]
            return orderbook

        except Exception as e:
            print (e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "ticker/publicSignV2"
            data = {"pairName": symbol}
            response = requests.post(url, data=data)
            return float(response.json()["data"][symbol]["nowPrice"])
        except Exception as e:
            print (e)

    def get_trades(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "ticker/publicSign"
            data = {"pairName": symbol}
            response = requests.post(url, data=data)
            trades = []
            for i in response.json()["data"]:
                trade = i.split("|")
                trade_type = "buy"
                if trade[0] == "ask":
                    trade_type = "sell"
                trades.append({
                    "type": trade_type,
                    "price": trade[1],
                    "count": trade[2],
                    "order_time": trade[3]
                })
            return trades
        except Exception as e:
            print (e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/coinzeus_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(symbols_details[symbol]["price_max_precision"])
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["quote_increment"])
        except Exception as e:
            print(e)


if __name__ == "__main__":
    coinzeus_public = CoinzeusPublic("https://api2.coinzeus.io/")
    orderbook = coinzeus_public.get_orderbook("WPC_BTC")
    # print orderbook
    # print len(orderbook["sellList"])
    # print len(orderbook["buyList"])
    # print coinzeus_public.get_price("WPC_BTC")
    # print coinzeus_public.get_precision("WPC_BTC")
    # print coinzeus_public.get_trades("WPC_BTC")

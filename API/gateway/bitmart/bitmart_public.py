from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import json
import math
import time
from Gateway.bitmart.archived.api_spot import APISpot

class BitmartPublic(object):
    def __init__(self, urlbase):
        self.spotAPI = APISpot("", "", "", url=urlbase)

    def load_symbols_details(self):
        try:
            current_path = path.dirname(path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/bitmart_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print("Bitmart public load symbols details error: %s" % e)

    def get_price_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(symbols_details[symbol]["price_max_precision"])
        except Exception as e:
            print("Bitmart public get price precision error: %s" % e)

    def get_price_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["quote_increment"])
        except Exception as e:
            print("Bitmart public get price increment error: %s" % e)

    def get_amount_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["base_min_size"])
        except Exception as e:
            print("Bitmart public get min amount error: %s" % e)

    def get_amount_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(abs(math.log10(float(symbols_details[symbol]["base_min_size"]))))
        except Exception as e:
            print("Bitmart public get amount precision error: %s" % e)

    def get_ticker(self, symbol):
        try:
            ticker, r = self.spotAPI.get_symbol_ticker(symbol)
            return ticker
        except Exception as e:
            print("Bitmart public get ticker error: %s" % e)

    def get_orderbook(self, symbol):
        try:
            maxPrecision = self.get_price_precision(symbol)
            result, r = self.spotAPI.get_symbol_book(symbol, maxPrecision)
            orderbook = {"buys": [], "sells": []}
            if result["code"] == 1000:
                orderbook = result["data"]
            else:
                mess = result["message"]
                print("Bitmart public error: %s" % mess)
            return orderbook
        except Exception as e:
            print("Bitmart public get orderbook error: %s" % e)

    def get_trades(self, symbol):
        try:
            result, r = self.spotAPI.get_symbol_trades(symbol)
            trades = []
            if result["code"] == 1000:
                trades = result["data"]["trades"]
            else:
                mess = result["message"]
                print("Bitmart public error: %s" % mess)
            return trades
        except Exception as e:
            print("Bitmart public get trades error: %s" % e)

    def get_price(self, symbol):
        try:
            price = 0.0
            trades = self.get_trades(symbol)
            if len(trades) > 0:
                price = float(trades[0]["price"])
            return price
        except Exception as e:
            print("Bitmart public get price error: %s" % e)

    def is_valid_price(self, symbol, price, amount):
        if "_ETH" in symbol and amount * price > 0.02:
            return True
        elif "_BTC" in symbol and amount * price > 0.0015:
            return True
        elif "_USDT" in symbol and amount * price > 5.0:
            return True
        return False

    def get_kline(self, symbol, timeperiod=300, interval=1):
        try:
            current_timestamp = int(time.time())
            from_timestamp = current_timestamp - timeperiod
            result, r = self.spotAPI.get_symbol_kline(symbol, from_timestamp, current_timestamp, interval)
            kline = []
            if result["code"] == 1000:
                kline = result["data"]["klines"]
            else:
                mess = result["message"]
                print("Bitmart public error: %s" % mess)
            return kline
        except Exception as e:
            print("Bitmart public get kline error: %s" % e)

if __name__ == "__main__":
    bitmart_public = BitmartPublic("https://api-cloud.bitmart.com")
    # print (bitmart_public.get_amount_precision("BTC_USDT"))
    # price = bitmart_public.get_ticker("BTC_USDT")
    # print(price)
    print(bitmart_public.get_trades('BTC_USDT'))
    # price = bitmart_public.get_price("BTC_USDT")
    # print(price)
    # orderbook = bitmart_public.get_orderbook("BTC_USDT")
    # print(orderbook)
    # kline = bitmart_public.get_kline("SG_USDT", timeperiod=604800*2, interval=1440)
    # print(kline)
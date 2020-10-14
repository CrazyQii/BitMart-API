import re
import requests
import os
import json
import time

class HotbitPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "/" + symbol_quote
        except Exception as e:
            print (e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/hotbit_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_price_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(symbols_details[symbol]["price_max_precision"])
        except Exception as e:
            print(e)

    def get_price_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["quote_increment"])
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market.last?market=%s" % (symbol)
            response = requests.get(url)
            return float(response.json()["result"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "order.depth?market=%s&limit=100&interval=1e-10" % (symbol)
            response = requests.get(url)
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in response.json()["result"]["bids"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in response.json()["result"]["asks"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            # full size of the orderbook is 100
            return orderbook
        except Exception as e:
            print (e)

    def get_kline(self, symbol, timeperiod=360, interval=60):
        try:
            symbol = self.symbol_convert(symbol)
            current_timestamp = int(time.time())
            from_timestamp = current_timestamp - timeperiod
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market.kline?market=%s&start_time=%s&end_time=%s&interval=%s" % (symbol, str(from_timestamp), str(current_timestamp), interval)
            response = requests.get(url)
            # print response.content
            return response.json()
        except Exception as e:
            print (e)
            
    def get_trades(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    hotbit_public = HotbitPublic("https://api.hotbit.io/api/v1/")
    print (hotbit_public.get_orderbook("BTC_USDT"))
    print(hotbit_public.get_kline("BTC_USDT"))

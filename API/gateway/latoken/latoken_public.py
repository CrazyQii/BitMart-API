from os import sys, path
import os
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import requests
import time
import re

class LatokenPublic(object):
    def __init__(self, urlbase, api_key, api_secret):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol = ''.join(symbol_pair)
            return symbol
        except Exception as e:
            print(e)

    def get_last_trade(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "MarketData/trades/%s/%s" % (symbol, 1)
            response = requests.get(url).content.decode('utf-8')
            response = json.loads(response)
            return response["trades"]
        except Exception as e:
            print("get_last_trade" + str(e))

    def get_price(self, symbol):
        try:
            return self.get_last_trade(symbol)[0]["price"]
        except Exception as e:
            print("get_price" + str(e))

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "MarketData/orderBook/%s/%s" % (symbol, 40)
            response = requests.get(url).content.decode('utf-8')
            response = json.loads(response)
            buys, sells = [], []
            for order in response["asks"]:
                sells.append({"count": 1, 
                                "amount": order["quantity"],
                                "total": order["price"] * order["quantity"], 
                                "price": order["price"]})
            for order in response["bids"]:
                buys.append({"count": 1, 
                                "amount": order["quantity"],
                                "total": order["price"] * order["quantity"], 
                                "price": order["price"]})
            return {"sells": sells, "buys": buys}
        except Exception as e:
            print("get_orderbook" + str(e))

    def dump_json(self, data):
        try:
            is_file = os.path.isfile("latoken_symbols_details.json")
            path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "latoken_symbols_details.json")
            with open(path, "w+") as f:
                symbols_details = json.dumps(data, indent = 4)
                f.write(symbols_details)
            f.close()
        except Exception as e:
            print(e)

    def save_pair_details_to_json(self):
        try:
            url = self.urlbase + "ExchangeInfo/pairs"
            response = json.loads(requests.get(url).content.decode('utf-8'))
            self.dump_json(response)
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/latoken_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            for pair in symbols_details:
                if pair["symbol"] == ''.join(symbol.split('_')):
                    price_tick = int(pair["pricePrecision"])
                    return 1.0 / 10 ** (price_tick)
            return
        except Exception as e:
            print("get_quote_increment" + str(e))

    def get_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            for pair in symbols_details:
                if pair["symbol"] == ''.join(symbol.split('_')):
                    return int(pair["pricePrecision"])
            return
        except Exception as e:
            print("get_precision" + str(e))

    def get_amount_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            for pair in symbols_details:
                if pair["symbol"] == ''.join(symbol.split('_')):
                    return int(pair["amountPrecision"])
            return
        except Exception as e:
            print("get_amount_precision" + str(e))

if __name__ == "__main__":

    l_public = LatokenPublic(
        "https://api.latoken.com/api/v1/", "", "")
    # print(l_public.save_pair_details_to_json())
    # print(l_public.get_quote_increment("APL_BTC"))
    # print(l_public.get_precision("APL_BTC"))
    # print(l_public.get_price("APL_BTC"))
    # print(l_public.get_orderbook("APL_BTC"))
    # print(l_public.get_last_trade("APL_BTC"))

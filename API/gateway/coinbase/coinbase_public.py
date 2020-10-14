import re
import requests
import time
import os
import json
import datetime
import math

class CoinbasePublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))

    def dump_json(self, data, file_name):
        try:
            path = os.path.join(os.path.split(os.path.realpath(__file__))[0], file_name)
            with open(path, "w+") as f:
                data_json = json.dumps(data, indent = 4)
                f.write(data_json)
            f.close()
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "products/%s/trades" % (symbol)
            response = requests.get(url)
            return float(response.json()[0]["price"])

        except Exception as e:
            print(e)
            return None

    '''
    full==True  return top 50 bids and asks (aggregated)
    full==False return full order book (non-aggregated)
    '''
    def get_orderbook(self, symbol, full=False):
        try:
            level = 3 if full else 2
            symbol = self.symbol_convert(symbol)

            url = self.urlbase + "products/%s/book?level=%s" % (symbol, level)
            response = requests.get(url)
            data = response.json()
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["asks"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

    def get_symbols_details(self):
        url = self.urlbase + "products"
        response = requests.get(url)
        data = response.json()
        self.dump_json(data, "coinbase_symbols_details.json")

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/coinbase_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print (e)

    def get_precision(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            details = next(item for item in symbols_details if item["id"] == symbol)
            return int(math.log10(1/float(details["quote_increment"])))
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            details = next(item for item in symbols_details if item["id"] == symbol)
            return float(details["quote_increment"])
        except Exception as e:
            print (e)
    
    def get_trades(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "products/%s/trades" % (symbol)
            response = requests.get(url)
            results = []
            for trade in response.json():
                results.append({
                    "count": trade["size"], 
                    "amount": float(trade["size"]) * float(trade["price"]), 
                    "price": trade["price"], 
                    "type": trade["side"], 
                    "order_time": time.mktime(time.strptime(trade["time"], "%Y-%m-%dT%H:%M:%S.%fZ")) * 1000
                })
            return results
        except Exception as e:
            print (e)

if __name__ == "__main__":
    idax_public = CoinbasePublic("https://api.pro.coinbase.com/")
    # print(idax_public.get_price("BTC_USD"))
    # print(idax_public.get_orderbook("BTC_USD"))
    # print(idax_public.get_orderbook("BTC_USD", True))
    # print(idax_public.get_symbols_details())
    # print(idax_public.load_symbols_details())
    # print(idax_public.get_precision("BTC_USD"))
    # print(idax_public.get_quote_increment("BTC_USD"))
    # print(idax_public.get_trades("BTC_USD"))

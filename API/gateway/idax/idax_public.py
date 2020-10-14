import re
import requests
import time
import os
import json

class IdaxPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        try:
            url = self.urlbase + "ticker?pair=%s" % (symbol)
            response = requests.get(url)
            return float(response.json()["ticker"][0]["last"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "depth?pair=%s&size=20" % symbol
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

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/idax_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print (e)

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
            print (e)
    
    def get_trades(self, symbol):
        try:
            url = self.urlbase + "trades?pair=%s" % symbol
            response = requests.get(url)
            results = []
            for trade in response.json()["trades"]:
                results.append({
                    "count": trade["quantity"], 
                    "amount": float(trade["quantity"]) * float(trade["price"]), 
                    "price": trade["price"], 
                    "type": trade["maker"].lower(), 
                    "order_time": trade["timestamp"]
                })
            return results
        except Exception as e:
            print (e)

if __name__ == "__main__":
    idax_public = IdaxPublic("https://openapi.idax.pro/api/v2/")
    # print(idax_public.get_price("PIX_BTC"))
    # print(idax_public.get_orderbook("APL_ETH"))
    # print(idax_public.load_symbols_details())
    # print(idax_public.get_precision("APL_ETH"))
    # print(idax_public.get_quote_increment("APL_ETH"))
    # print(idax_public.get_trades("APL_ETH"))
# 
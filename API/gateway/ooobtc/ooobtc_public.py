import re
import requests
import time
import os
import json

class OoobtcPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_trades(self, symbol):
        try:
            url = self.urlbase + "public/v1/getorderhistory?kv=%s" % symbol
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print (e)

    def get_price(self, symbol):
        try:
            url = self.urlbase + "public/v1/getticker?kv=%s" % (symbol)
            response = requests.get(url)
            return float(response.json()["data"]["lastprice"])

        except Exception as e:
            print(e)
            return None
            
    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "public/v1/getorderbook?kv=%s" % symbol
            response = requests.get(url)
            data = response.json()
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["data"]["buy"]:
                tmp = {}
                tmp["price"] = float(i["price"])
                tmp["amount"] = float(i["number"])
                total_amount_buys += float(i["number"])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["data"]["sell"][::-1]:
                tmp = {}
                tmp["price"] = float(i["price"])
                tmp["amount"] = float(i["number"])
                total_amount_sells += float(i["number"])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/ooobtc_symbols_details.json", "r") as f:
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
            

if __name__ == "__main__":
    altilly_public = OoobtcPublic("https://openapi.ooobtc.com/")
    # print altilly_public.get_trades("LPK_ETH")
    # print altilly_public.get_price("LPK_ETH")
    # print altilly_public.get_orderbook("LPK_ETH")


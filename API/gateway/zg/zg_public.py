import re
import requests
import time
import os
import json

class ZgPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        return ''.join(symbol.split('_')) 

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/openapi/quote/v1/ticker/price?symbol=%s" % (symbol)
            response = requests.get(url)
            return float(response.json()["price"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/openapi/quote/v1/depth?symbol=%s" % symbol
            response = requests.get(url)
            data = response.json()
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            if data["bids"]:
                for i in data["bids"]:
                    tmp = {}
                    tmp["price"] = float(i[0])
                    tmp["amount"] = float(i[1])
                    total_amount_buys += float(i[1])
                    tmp["total"] = total_amount_buys
                    orderbook["buys"].append(tmp)
            if data["asks"]:
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
            with open(current_path + "/zg_symbols_details.json", "r") as f:
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
    
    def get_amount_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["amount_precision"])
        except Exception as e:
            print(e)
    
    def get_trades(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/openapi/quote/v1/trades?symbol=%s" % symbol
            response = requests.get(url)
            results = []
            for trade in response.json():
                results.append({
                    "count": trade["qty"],
                    "amount": float(trade["qty"]) * float(trade["price"]),
                    "price": trade["price"], 
                    "type": "buy" if trade["isBuyerMaker"] else "sell",
                    "order_time": trade["time"]/1000
                })
            return results
        except Exception as e:
            print (e)

if __name__ == "__main__":
    zg_public = ZgPublic("https://api.zg8.com")
    print(zg_public.get_price("BTC_USDT"))
    print(zg_public.get_orderbook("BTC_USDT"))
    # print(zg_public.load_symbols_details())
    # print(zg_public.get_precision("ZNC_USDT"))
    # print(zg_public.get_quote_increment("ZNC_USDT"))
    # print(zg_public.get_trades("BTC_USDT"))

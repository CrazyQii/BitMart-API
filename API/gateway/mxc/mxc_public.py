import re
import requests
import time
import datetime
import os
import json

class MxcPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        try:
            url = self.urlbase + "data/ticker?market=%s" % (symbol)
            response = requests.get(url)
            return float(response.json()["data"]["last"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "data/depth?market=%s&depth=20" % symbol
            response = requests.get(url)
            data = response.json()["data"]
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = float(i["price"])
                tmp["amount"] = float(i["quantity"])
                total_amount_buys += float(i["quantity"])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["asks"]:
                tmp = {}
                tmp["price"] = float(i["price"])
                tmp["amount"] = float(i["quantity"])
                total_amount_sells += float(i["quantity"])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

    def dump_json(self, data, file_name):
        try:
            is_file = os.path.isfile(file_name)
            path = os.path.join(os.path.split(os.path.realpath(__file__))[0], file_name)
            with open(path, "w+") as f:
                data_json = json.dumps(data, indent = 4)
                f.write(data_json)
            f.close()
        except Exception as e:
            print(e)

    def get_symbols_details(self):
        try:
            url = self.urlbase + "data/markets_info"
            response = requests.get(url).json()
            self.dump_json(response["data"], "mxc_markets_details.json")
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/mxc_markets_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print (e)

    def get_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(symbols_details[symbol]["priceScale"])
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(1.0 / 10 ** int(symbols_details[symbol]["priceScale"]))
        except Exception as e:
            print (e)
    
    def get_trades(self, symbol):
        try:
            url = self.urlbase + "data/history?market=%s" % symbol
            response = requests.get(url)
            results = []
            for trade in response.json()["data"]:
                results.append({
                    "count": trade["tradeQuantity"], 
                    "amount": float(trade["tradeQuantity"]) * float(trade["tradePrice"]), 
                    "price": trade["tradePrice"], 
                    "type": "buy" if trade["tradeType"] == "1" else "sell", 
                    "order_time": time.mktime(datetime.datetime.strptime(trade["tradeTime"], "%Y-%m-%d %H:%M:%S.%f").timetuple())
                })
            return results
        except Exception as e:
            print (e)

if __name__ == "__main__":
    mxc_public = MxcPublic("https://www.mxc.com/open/api/v1/")
    # print(mxc_public.get_price("GRIN_USDT"))
    # print(mxc_public.get_orderbook("GRIN_USDT"))
    # print(mxc_public.get_symbols_details())
    # print(mxc_public.load_symbols_details())
    # print(mxc_public.get_precision("GRIN_USDT"))
    # print(mxc_public.get_quote_increment("GRIN_USDT"))
    # print(mxc_public.get_trades("GRIN_USDT"))

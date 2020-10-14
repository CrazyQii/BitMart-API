import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import json
import requests
import time

class LbankPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/lbank_symbols_details.json", "r") as f:
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
            return int(abs((symbols_details[symbol]["base_min_size"])))
        except Exception as e:
            print(e)

    def get_ticker(self, symbol):
        url = self.urlbase + "v2/ticker.do?symbol=%s" % symbol.lower()
        content = requests.request("GET", url)
        content = content.json()["data"][0]["ticker"]
        dict = {}
        dict['volume'] = content["vol"]
        dict['ask_1'] = None
        dict['lowest_price'] = content["low"]
        dict['bid_1'] = None
        dict['highest_price'] = content["high"]
        dict['base_volume'] = content["turnover"]
        dict['current_price'] = content["latest"]
        dict['fluctuation'] = content["change"]
        dict['symbol_id'] = symbol
        return dict

    def get_price(self, symbol):
        try:
            ticker = self.get_ticker(symbol)
            return ticker["current_price"]
        except Exception as e:
            print(e)
            return None

    def get_trades(self, symbol):
        try:
            url = self.urlbase + "v2/trades.do?symbol=%s&size=100" % symbol.lower()
            response = requests.get(url)
            results = []
            for trade in response.json()["data"]:
                results.append({
                    "count": trade["amount"],
                    "amount": float(trade["amount"]) * float(trade["price"]),
                    "price": trade["price"],
                    "type": trade["type"],
                    "order_time": trade["date_ms"]
                })
            return results
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "v2/depth.do?symbol=%s&size=60&merge=0" % symbol.lower()
            response = requests.get(url)
            data = response.json()["data"]
            buys, sells = [], []
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                buys.append(tmp)
            for i in data["asks"]:#[::-1]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                sells.append(tmp)
            return {"buys": buys, "sells": sells}
        except Exception as e:
            print(e)
            return {"buys":[], "sells":[]}

if __name__ == "__main__":
    lbank_public = LbankPublic("https://api.lbkex.com/")
    # print(lbank_public.get_ticker("BTC_USDT"))
    # print(lbank_public.get_price("BTC_USDT"))
    # print(lbank_public.get_orderbook("BTC_USDT"))
    # print(lbank_public.get_trades("BTC_USDT"))
    # print(lbank_public.get_precision("HEX_USDT"))
    # print(lbank_public.get_quote_increment("HEX_USDT"))

    
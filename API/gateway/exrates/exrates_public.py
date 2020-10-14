import re
import requests
import time
import os
import json
from datetime import datetime

class ExratesPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        try:
            url = self.urlbase + "public/ticker?currency_pair=%s" % (symbol.lower())
            response = requests.get(url)
            return float(response.json()[0]["last"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "public/orderbook/%s" % symbol.lower()
            response = requests.get(url)
            data = response.json()
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["BUY"]:
                tmp = {}
                tmp["price"] = float(i["rate"])
                tmp["amount"] = float(i["amount"])
                total_amount_buys += float(i["amount"])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["SELL"]:
                tmp = {}
                tmp["price"] = float(i["rate"])
                tmp["amount"] = float(i["amount"])
                total_amount_sells += float(i["amount"])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

    def get_trades(self, symbol):
        try:
            from_date = to_date = datetime.today().strftime('%Y-%m-%d')
            url = self.urlbase + "public/history/%s?from_date=%s&to_date=%s" % (symbol.lower(), from_date, to_date)
            response = requests.get(url)
            results = []
            for trade in response.json()["body"]:
                results.append({
                    "count": trade["amount"], 
                    "amount": float(trade["amount"]) * float(trade["price"]), 
                    "price": trade["price"], 
                    "type": trade["order_type"].lower(), 
                    "order_time": trade["date_creation"]
                })
            return results
        except Exception as e:
            print (e)

if __name__ == "__main__":
    start = time.time()
    ex_public = ExratesPublic("https://api.exrates.me/openapi/v1/")
    # print(ex_public.get_price("BTC_USDT"))
    # print(ex_public.get_orderbook("BTC_USDT"))
    # print(ex_public.get_trades("BTC_USDT"))
    end = time.time()
    print(end - start)
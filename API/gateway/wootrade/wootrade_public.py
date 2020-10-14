import os
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hmac
import hashlib
import math
import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode

class WootradePublic(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/wootrade_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def symbol_convert(self, symbol):
        return "SPOT_" + symbol

    def sign_message(self, data):
        try:
            return hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            last_trade = self.get_trades(symbol, 1)
            return last_trade[0]["price"]
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/orderbook/%s?max_level=%s" % (symbol, 30)
            ts = str(time.time())
            msg = "max_level=30|" + str(ts)
            sign = self.sign_message(msg)

            header = {"Content-Type": "application/x-www-form-urlencoded", 
                        "x-api-key": self.apikey,
                        "x-api-signature": sign,
                        "x-api-timestamp": ts,
                        "cache-control": "no-cache"}
            response = requests.request("GET", url, headers=header)

            data = response.json()
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = i["price"]
                tmp["amount"] = i["quantity"]
                total_amount_buys += i["quantity"]
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["asks"]:#[::-1]:
                tmp = {}
                tmp["price"] = i["price"]
                tmp["amount"] = i["quantity"]
                total_amount_sells += i["quantity"]
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

    def get_precision(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            return -int(math.log10(symbols_details[symbol]["quote_tick"]))
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["quote_tick"])
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            return -int(math.log10((symbols_details[symbol]["base_min"])))
        except Exception as e:
            print(e)

    ## ticker not supported
    # def get_ticker(self, symbol):
    #     symbol = self.symbol_convert(symbol)
    #     url = self.urlbase + "get-ticker?market=%s" % symbol
    #     content = requests.request("GET", url)
    #     content = content.json()['data']
    #     dict = {}
    #     dict['volume'] = content['volume']
    #     dict['ask_1'] = content['askPrice']
    #     dict['lowest_price'] = content['lowPrice']
    #     dict['bid_1'] = content['bidPrice']
    #     dict['highest_price'] = content['highPrice']
    #     dict['base_volume'] = content['baseVolume']
    #     dict['current_price'] = content['lastPrice']
    #     dict['fluctuation'] = content['change24h']
    #     dict['symbol_id'] = content['symbol'].upper()
    #     return dict

    def get_trades(self, symbol, limit = 50):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/public/market_trades?symbol=%s&limit=%s" % (symbol, limit)
            response = requests.get(url)
            results = []
            for trade in response.json()["rows"]:
                results.append({
                    "count": trade["executed_quantity"],
                    "amount": float(trade["executed_quantity"]) * float(trade["executed_price"]),
                    "price": trade["executed_price"],
                    "type": trade["side"].lower(),
                    "order_time": trade["executed_timestamp"]
                })
            return results
        except Exception as e:
            print(e)


if __name__ == "__main__":
    w_public = WootradePublic("https://nexus.kronostoken.com/",
                                "AbmyVJGUpN064ks5ELjLfA==", 
                                "QHKRXHPAW1MC9YGZMAT8YDJG2HPR")
    print(w_public.get_price("BTC_USDT"))
    # print(w_public.get_ticker("BTC_USDT"))
    print(w_public.get_orderbook("BTC_USDT"))
    print(w_public.get_precision("BTC_USDT"))
    print(w_public.get_quote_increment("BTC_USDT"))
    print(w_public.get_amount_precision("BTC_USDT"))
    print(w_public.get_trades("BTC_USDT"))
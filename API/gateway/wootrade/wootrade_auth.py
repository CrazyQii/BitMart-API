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


class WootradeAuth(object):
    def __init__(self, urlbase, api_key, api_secret,password=""):
        self.apikey = api_key
        self.urlbase = urlbase
        self.secret = api_secret

    def symbol_convert(self, symbol):
        return "SPOT_" + symbol

    def sign_message(self, data):
        try:
            return hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        except Exception as e:
            print(e)

    def output(self, function_name, content):
        info = {
            "func_name": function_name,
            "response": content.json()
        }
        print(info)

    def load_symbols_details(self):
        try:
            current_path = path.dirname(path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/wootrade_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            #symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            return -int(math.log10((symbols_details[symbol]["base_min"])))
        except Exception as e:
            print(e)

    def get_precision(self, symbol):
        try:
            #symbol = self.symbol_convert(symbol)
            symbols_details = self.load_symbols_details()
            return -int(math.log10(symbols_details[symbol]["quote_tick"]))
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        symbol = self.symbol_convert(symbol)
        ts = int(time.time()*1000)
        price_precision = self.get_precision(symbol)#".8f"
        price = round(price, price_precision)        
        order = dict()
        order['symbol'] = symbol
        order['order_quantity'] = amount
        order['order_price'] = price
        order['side'] = side.upper()
        order["order_type"] = "LIMIT"

        msg = ''
        for key in sorted(order.keys()):
            msg += ('&' + key + "=" +str(order[key]))
        msg = msg[1:]
        url = self.urlbase + ("v1/order" + "?" + msg)
        msg += ("|" + str(ts))
        print(url, msg)
        sign = self.sign_message(msg)
        header = {"Content-Type": "application/x-www-form-urlencoded", 
                    "x-api-key": self.apikey,
                    "x-api-signature": sign,
                    "x-api-timestamp": str(ts),
                    "cache-control": "no-cache"}
        response = requests.request("POST", url, data=order, headers=header)
        print(response.json())
        if response.json()["success"]:
            return response.json()["order_id"]
        else:
            print(response.json()["success"])

    def cancel_order(self, symbol, entrust_id):
        symbol = self.symbol_convert(symbol)
        ts = int(time.time())

        order = dict()
        order['symbol'] = symbol
        order['order_id'] = entrust_id

        msg = ''
        for key in sorted(order.keys()):
            msg += ('&' + key + "=" +str(order[key]))
        msg = msg[1:]
        url = self.urlbase + ("v1/order" + "?" + msg)
        msg += ("|" + str(ts))
        sign = self.sign_message(msg)
        header = {"Content-Type": "application/x-www-form-urlencoded", 
                    "x-api-key": self.apikey,
                    "x-api-signature": sign,
                    "x-api-timestamp": str(ts),
                    "cache-control": "no-cache"}
        response = requests.request("DELETE", url, data=order, headers=header)

        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": response.json()["success"]
        }
        print(info)

    def open_orders(self, symbol, status="INCOMPLETE"):
        symbol = self.symbol_convert(symbol)
        ts = int(time.time())

        order = dict()
        order['symbol'] = symbol
        order['status'] = status

        msg = ''
        for key in sorted(order.keys()):
            msg += ('&' + key + "=" +str(order[key]))
        msg = msg[1:]
        url = self.urlbase + ("v1/orders" + "?" + msg)
        msg += ("|" + str(ts))
        sign = self.sign_message(msg)
        header = {"Content-Type": "application/x-www-form-urlencoded", 
                    "x-api-key": self.apikey,
                    "x-api-signature": sign,
                    "x-api-timestamp": str(ts),
                    "cache-control": "no-cache"}
        response = requests.request("GET", url, headers=header)

        order_list = []
        try:
            for i in response.json()["rows"]:
                order_list.append({
                    "symbol": i['symbol'],
                    "entrust_id": i["order_id"],
                    "price": i["price"],
                    "side": i["side"].lower(),
                    "original_amount": float(i["quantity"]),
                    "remaining_amount": float(i["quantity"]) - float(i["executed"]),
                    "timestamp": i["created_time"]
                })
            return order_list
        except Exception as e:
            print(e)

    def order_detail(self, symbol, id):
        symbol = self.symbol_convert(symbol)
        ts = int(time.time())

        order = dict()
        order['oid'] = id

        msg = ''
        for key in sorted(order.keys()):
            msg += ('&' + key + "=" +str(order[key]))
        msg = msg[1:]
        url = self.urlbase + ("v1/order" + "?" + msg)
        msg += ("|" + str(ts))
        sign = self.sign_message(msg)
        header = {"Content-Type": "application/x-www-form-urlencoded", 
                    "x-api-key": self.apikey,
                    "x-api-signature": sign,
                    "x-api-timestamp": str(ts),
                    "cache-control": "no-cache"}
        response = requests.request("GET", url, data=data, headers=header)
        trade = response.json()
        try:                
            return {"symbol": trade['symbol'],
                    "entrust_id": trade["order_id"],
                    "price": trade["price"],
                    "side": trade["side"].lower(),
                    "original_amount": float(trade["quantity"]),
                    "remaining_amount": float(trade["quantity"]) - float(trade["executed"]),
                    "timestamp": trade["created_time"]
                    }
        except Exception as e:
            print(e)

    def wallet_balance(self):
        url = self.urlbase + "v2/client/holding?all=true"
        ts = int(time.time())
        msg = "all=true|" + str(ts)
        sign = self.sign_message(msg)
        header = {"Content-Type": "application/x-www-form-urlencoded", 
                    "x-api-key": self.apikey,
                    "x-api-signature": sign,
                    "x-api-timestamp": str(ts),
                    "cache-control": "no-cache"}
        response = requests.request("GET", url, headers=header)
        free, frozen = {} ,{}
        try:
            for coin in response.json()["holding"]:
                #if coin["holding"] != 0 and coin["frozen"] != 0:
                symbol = coin["token"]
                free[symbol] = coin["holding"]
                frozen[symbol] = coin["frozen"]
            return free, frozen
        except Exception as e:
            print(e)

    def wallet_info(self):
        url = self.urlbase + "v1/client/info"
        ts = int(time.time())
        msg = "|" + str(ts)
        sign = self.sign_message(msg)
        header = {"Content-Type": "application/x-www-form-urlencoded", 
                    "x-api-key": self.apikey,
                    "x-api-signature": sign,
                    "x-api-timestamp": str(ts),
                    "cache-control": "no-cache"}
        response = requests.request("GET", url, headers=header)
        balance_info = {}
        try:
            if response.json()["success"]:
                balance_info = response.json()["application"]
            return balance_info
        except Exception as e:
            print(e)

if __name__ == "__main__":
    w_auth = WootradeAuth("https://nexus.kronostoken.com/",
                                "x31EVa5ZXcb5KZkfEDpQow==", 
                                "E2GS90V0K4MF8WGT48TRP3MQXJY9")
    # print(w_auth.place_order("BTC_USDT", 0.002, 6683.0, "sell"))
    # print(w_auth.wallet_balance())
    # print(w_auth.wallet_info())
    # o = w_auth.open_orders("BTC_USDT")
    # for i in o:
    #     w_auth.cancel_order("BTC_USDT", i["entrust_id"])
    # print(w_auth.order_detail("dd3164b333a4afa9d5730bb87f6db8b3"))

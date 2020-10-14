from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
# from keys.bitmart_fundbalance_key import fcoin_key
import json
import re
import requests
import time
import hmac
import hashlib
import random
import traceback
import base64
import math

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class FcoinAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def symbol_convert(self, symbol):
        return ''.join(symbol.split('_')).lower()

    def sign_message(self, timestamp, method, path, data):
        try:
            message = (method.upper() + path + timestamp + data).encode("utf-8")
            message = base64.b64encode(message)
            signature = hmac.new(self.secret.encode("utf-8"), message, hashlib.sha1)
            signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
            return signature_b64
        except Exception as e:
            print (e)

    def request(self, method, path, data=None, headers=None):

        try:
            resp = requests.request(method, path, data=data, headers=headers)

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    "url": path,
                    "method": method,
                    "data": data,
                    "code": resp.status_code,
                    "msg": resp.text
                }
                return False, error
        except Exception as e:
            error = {
                "url": path,
                "method": method,
                "data": data,
                "traceback": traceback.format_exc(),
                "error": e
            }
            return False, error

    def output(self, function_name, content):
        info = {
            "func_name": function_name,
            "response": content
        }
        print (info)
    
    def load_symbols_details(self):
        try:
            current_path = path.dirname(path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/fcoin_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            symbol_details = self.load_symbols_details()
            details = next(item for item in symbols_details if item["id"] == symbol)
            return details["amount_decimal"]
        except Exception as e:
            print (e)

    def place_order(self, symbol, amount, price, side):
        url = self.urlbase + "orders"
        timestamp = str(int(time.time() * 1000))

        data = {
                "type": "limit",
                "amount": amount,
                "price": price,
                "side": side,
                "symbol": self.symbol_convert(symbol),
                "exchange": "main"
        }

        sign_data = ""
        for key in sorted(data):
            sign_data += (key + "=" + str(data[key]) + "&")
        sign_data = sign_data[0: len(sign_data) - 1]

        sign = self.sign_message(timestamp, "POST", url, sign_data)
        data = json.dumps(data)
        headers = {
            "Content-Type": "Application/JSON", 
            "FC-ACCESS-KEY": self.apikey,
            "FC-ACCESS-SIGNATURE": sign,
            "FC-ACCESS-TIMESTAMP": timestamp
            }
        
        is_ok, content = self.request("POST", url, data, headers)
        if is_ok:
            return content["data"]
        else:
            self.output("place_order", content)

    def cancel_order(self, symbol, entrust_id):
        url = self.urlbase + "orders/" + str(entrust_id) + "/submit-cancel"
        timestamp = str(int(time.time() * 1000))

        # data = {
        #         "order_id": entrust_id
        # }
        data = {}

        sign_data = ""
        for key in sorted(data):
            sign_data += (key + "=" + str(data[key]) + "&")
        sign_data = sign_data[0: len(sign_data) - 1]

        sign = self.sign_message(timestamp, "POST", url, sign_data)
        data = json.dumps(data)
        headers = {
            "Content-Type": "Application/JSON", 
            "FC-ACCESS-KEY": self.apikey,
            "FC-ACCESS-SIGNATURE": sign,
            "FC-ACCESS-TIMESTAMP": timestamp
            }
        
        is_ok, content = self.request("POST", url, data, headers)
        if is_ok:
            return True
        else:
            self.output("cancel_order", content)

    def order_detail(self, entrust_id):
        url = self.urlbase + "orders/" + str(entrust_id)
        timestamp = str(int(time.time() * 1000))

        data = {}

        sign_data = ""
        for key in sorted(data):
            sign_data += (key + "=" + str(data[key]) + "&")
        sign_data = sign_data[0: len(sign_data) - 1]

        sign = self.sign_message(timestamp, "GET", url, sign_data)
        data = json.dumps(data)
        headers = {
            "Content-Type": "Application/JSON", 
            "FC-ACCESS-KEY": self.apikey,
            "FC-ACCESS-SIGNATURE": sign,
            "FC-ACCESS-TIMESTAMP": timestamp
            }

        is_ok, content = self.request("GET", url, data, headers)
        if is_ok:
            return ({
                "symbol": content["data"]["product_id"].upper(),
                "entrust_id": content["data"]["id"],
                "price": content["data"]["price"], 
                "side": content["data"]["side"],
                "original_amount": content["data"]["amount"],
                "remaining_amount": float(content["data"]["amount"]) - float(content["data"]["filled_amount"]),
                "timestamp": content["data"]["created_at"]
            })
        else:
            self.output("order_detail", content)

    def open_orders(self, symbol):
        sub_orders = self.open_order(symbol, "submitted")
        part_orders = self.open_order(symbol, "partial_filled")
        orders = []
        if sub_orders:
            orders.extend(sub_orders)
        if part_orders:
            orders.extend(part_orders)
        return orders

    def open_order(self, symbol, states):
        url = self.urlbase + "orders"
        timestamp = str(int(time.time() * 1000))

        data = {
                "symbol": self.symbol_convert(symbol),
                "states": states
        }

        sign_data = ""
        for key in sorted(data):
            sign_data += (key + "=" + str(data[key]) + "&")
        sign_data = sign_data[0: len(sign_data) - 1]
        url = url + "?" + sign_data

        sign = self.sign_message(timestamp, "GET", url, "")
        data = json.dumps(data)
        headers = {
            "Content-Type": "Application/JSON", 
            "FC-ACCESS-KEY": self.apikey,
            "FC-ACCESS-SIGNATURE": sign,
            "FC-ACCESS-TIMESTAMP": timestamp
            }

        is_ok, content = self.request("GET", url, data, headers)
        if is_ok:
            orders = []
            for order in content["data"]:
                orders.append({
                "symbol": symbol,
                "entrust_id": order["id"],
                "price": order["price"], 
                "side": order["side"],
                "original_amount": order["amount"],
                "remaining_amount": float(order["amount"]) - float(order["filled_amount"]),
                "timestamp": order["created_at"]
                })
            return orders
        else:
            self.output("order_detail", content)

    def wallet_balance(self):
        url = self.urlbase + "accounts/balance"
        timestamp = str(int(time.time() * 1000))

        data = ""
        sign = self.sign_message(timestamp, "GET", url, data)

        headers = {
            "FC-ACCESS-KEY": self.apikey,
            "FC-ACCESS-SIGNATURE": sign,
            "FC-ACCESS-TIMESTAMP": timestamp
            }

        is_ok, content = self.request("GET", url, None, headers)
        if is_ok:
            free, frozen = {}, {}
            for coin in content["data"]:
                if float(coin["available"]) >= 0.0 or float(coin["frozen"]) > 0.0:
                    # print(coin)
                    free[coin["currency"].upper()] = float(coin["available"])
                    frozen[coin["currency"].upper()] = float(coin["frozen"])
            return free, frozen
        else:
            self.output("wallet_balance", content)

if __name__ == "__main__":
    cb_auth = FcoinAuth("https://api.fcoin.com/v2/", fcoin_key["api_key"], fcoin_key["api_secret"])
    # orderid1 = cb_auth.place_order("FT_USDT", 100, 0.0275, "sell")
    # print (orderid1)
    # orderid2 = cb_auth.place_order("BTC_USDT", 145, 0.0000108, "buy")
    # print(cb_auth.open_orders("FT_USDT"))
    # ods = cb_auth.open_orders("FT_USDT")
    # print(ods)
    # for o in ods:
    #     cb_auth.cancel_order(o["entrust_id"])
    # print(cb_auth.order_detail(orderid1))
    # print(cb_auth.cancel_order(orderid1))
    # print(cb_auth.cancel_order(orderid2))
    # print(cb_auth.order_detail(orderid1))
    print(cb_auth.wallet_balance())
    # print(cb_auth.open_orders("FT_USDT"))
    # print(cb_auth.order_detail("BTC_USDT", orderid1))
    # print(cb_auth.order_detail("BTC_USDT", orderid2))
    # print(cb_auth.in_order_list("BTC_USDT"))
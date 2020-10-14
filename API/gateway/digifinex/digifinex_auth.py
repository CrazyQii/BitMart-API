from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hmac
import hashlib

from key.digifinex_token import apl
import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class DigiFinexAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def get_server_time(self):
        url = self.urlbase + "time"
        response = requests.get(url)

        return response.json()["server_time"]

    def sign_message(self, data):
        try:
            if data == None:
                query_string = ''
            else:
                query_string = '&'.join(["{}={}".format(k, v) for k, v in data.items()])
            m = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
            s = m.hexdigest()
            # print("data-origin:", data)
            # print("query_string:", query_string)
            # print("sign:", s)
            return s
        except Exception as e:
            print(e)

    def request(self, method, path, data=None, needSign = True):
        try:
            if needSign:
                response = requests.request(method, self.urlbase + path, data=data, headers={
                    "ACCESS-KEY": self.apikey,
                    "ACCESS-TIMESTAMP": str(self.get_server_time()),
                    "ACCESS-SIGN": self.sign_message(data),
                })
            else:
                response = requests.request(method, self.urlbase + path, data=data)

            return response

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
            "response": content.json()
        }
        print(info)

    def load_symbols_details(self):
        try:
            current_path = path.dirname(path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/digifinex_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            symbol_details = self.load_symbols_details()
            return int(symbol_details[symbol]["amount_precision"])
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        url = "spot/order/new"

        # amount_precision = self.get_amount_precision(symbol)
        # amount_precision = "." + str(amount_precision) + "f"
        # amount = format(amount, amount_precision)
        price_precision = self.get_amount_precision(symbol)
        price_precision = ".8f"
        price = format(price, price_precision)

        data = {"symbol": symbol.lower(), "price": price, "amount": amount,
                "type": side}
        content = self.request("POST", url, data)
        self.output("place_order", content)
        if content.json()["code"] == 0:
            return content.json()['order_id']

    def cancel_order(self, entrust_id):
        url = "spot/order/cancel"

        data = {"order_id": entrust_id}

        content = self.request("POST", url, data)

        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": content.json()
        }
        print(info)

    def open_orders(self, symbol):
        url = "spot/order/current"

        # data = {"symbol": symbol.lower()
        #     # ,
        #     #     "limit": 100,
        #     #     "start_time": self.get_server_time() - 60 * 60 * 24 * 30,
        #     #     "end_time": self.get_server_time()
        #         }

        content = self.request("GET", url)
        # print(content.json())

        order_list = []
        try:
            for i in content.json()["data"]:
                order_list.append({
                    "symbol": i['symbol'],
                    "entrust_id": i["order_id"],
                    "price": i["price"],
                    "side": i["type"],
                    "original_amount": i["amount"],
                    "remaining_amount": i["amount"] - i['executed_amount'] * i['price'],
                    "timestamp": i["created_date"]
                })
            return order_list

        except Exception as e:
            print(e)

    def order_detail(self, id):
        url = "spot/order"

        data = {
            "order_id": id
        }

        content = self.request("GET", url, data)
        # print(content.json())

        order_list = []
        try:
            for i in content.json()["data"]:
                order_list.append({
                    "symbol": i['symbol'],
                    "entrust_id": i["order_id"],
                    "price": i["price"],
                    "side": i["type"],
                    "original_amount": i["amount"],
                    "remaining_amount": i["amount"] - i['executed_amount'] * i['price'],
                    "timestamp": i["created_date"]
                })

            return order_list
        except Exception as e:
            print(e)


    # def open_orders(self, symbol):
    #     url = self.urlbase + "orderHistory"
    #     timestamp = self.get_server_time()
    #     headers = {"Content-Type": "application/json"}
    #     orderState = 0
    #     currentPage = 1
    #     pageLength = 100

    #     data = {"key": self.apikey, "pair": symbol, "orderState": orderState, "currentPage": currentPage, "pageLength": pageLength, "timestamp": timestamp}

    #     sign = self.sign_message(data)
    #     data["sign"] = sign
    #     data = json.dumps(data)

    #     is_ok, content = self.request("POST", url, data, headers)

    #     if is_ok:
    #         return content
    #     else:
    #         self.output("open_orders", content)

    def wallet_balance(self):

        content = self.request("GET", "spot/assets")
        self.output("wallet_balance", content)


if __name__ == "__main__":
    d_auth = DigiFinexAuth("https://openapi.digifinex.vip/v3/", apl["api_key"], apl["api_secret"])
    # d_auth.place_order("APL_ETH", 70586, 0.0000066, "sell")
    d_auth.wallet_balance()
    o = d_auth.open_orders("")
    for i in o:
        d_auth.cancel_order(i["entrust_id"])
    # print(d_auth.order_detail("dd3164b333a4afa9d5730bb87f6db8b3"))

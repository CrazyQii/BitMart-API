import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import datetime
import hashlib
import hmac

import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class yobitAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def sign_message(self, data):
        try:
            data['nonce'] = int(time.time())
            sign = hmac.new(self.secret.encode(),
                            urlencode(data).encode(),
                            hashlib.sha512).hexdigest()
            return sign
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
            with open(current_path + "/yobit_symbols_details.json", "r") as f:
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
        url = "https://yobit.net/tapi/"
        price_precision = ".8f"
        price = format(price, price_precision)

        order = dict()
        order["method"] = "Trade"
        order['pair'] = symbol.lower()
        order['amount'] = int(amount)
        order['rate'] = price
        order['type'] = side

        sign = self.sign_message(order)
        header = {"Key": self.apikey, 
                    "Sign": sign, 
                    'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=order, headers=header)

        if str(response.json()["success"]) == "1":
            return response.json()["return"]['order_id']
        else:
            print(response.json())

    def cancel_order(self, symbol, entrust_id):
        url = "https://yobit.net/tapi/"

        order = {"method": "CancelOrder",
                 "order_id": entrust_id}

        sign = self.sign_message(order)
        header = {"Key": self.apikey, 
                    "Sign": sign, 
                    'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=order, headers=header)

        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": response.json()
        }
        print(info)

    def open_orders(self, symbol):
        url = "https://yobit.net/tapi/"

        data = {"method": "ActiveOrders",
                 "pair": symbol.lower()
                }

        sign = self.sign_message(data)
        header = {"Key": self.apikey, 
                    "Sign": sign, 
                    'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=data, headers=header)
        if response.json()["success"] == 1 and "return" not in response.json().keys():
            return []
        else:
            orders = response.json()["return"]
            order_list = []
            try:
                for oid in orders.keys():
                    order_list.append({
                        "symbol": symbol,
                        "entrust_id": oid,
                        "price": orders[oid]["rate"],
                        "side": orders[oid]["type"],
                        "original_amount": orders[oid]["amount"],
                        "remaining_amount": orders[oid]["amount"],
                        "timestamp": orders[oid]["timestamp_created"]
                    })
                return order_list

            except Exception as e:
                print(e)

    def order_detail(self, symbol, entrustId):
        url = "https://yobit.net/tapi/"

        data = {"method": "OrderInfo",
                 "order_id": entrustId
                }        

        sign = self.sign_message(data)
        header = {"Key": self.apikey, 
                    "Sign": sign, 
                    'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=data, headers=header)

        try:
            order = response.json()["return"][str(entrustId)]
            return ({
                "symbol": symbol,
                "entrust_id": entrustId,
                "price": order["rate"],
                "side": order["type"],
                "original_amount": order["start_amount"],
                "remaining_amount": order["amount"],
                "timestamp": order["timestamp_created"]
            })
        except Exception as e:
            print(e)

    def wallet_balance(self):
        url = "https://yobit.net/tapi/"
        data = {
            "method": "getInfo",
        }
        sign = self.sign_message(data)
        header = {"Key": self.apikey, 
                    "Sign": sign, 
                    'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=data, headers=header).json()["return"]
        results = []
        free, frozen = {} ,{}
        if "funds" in response.keys():
            for coin in response["funds"].keys():
                free[coin.upper()] = response["funds"][coin]
        if "funds_incl_orders" in response.keys():
            for coin in response["funds_incl_orders"].keys():
                frozen[coin.upper()] = response["funds_incl_orders"][coin] - response["funds"][coin]
        return free, frozen

if __name__ == "__main__":
    ybt_auth = yobitAuth("", 
        "6BC497FF237CF2B706EDB3FEF9FC130A",
        "229118e8df386b8da9690c630cc1b6d7")
    # print(ybt_auth.place_order("HEX_BTC", 1000, 0.00000030, "sell"))
    # print(ybt_auth.wallet_balance())
    # order1 = ybt_auth.place_order("HEX_BTC", 20, 0.00095, "buy")
    # order2 = ybt_auth.place_order("HEX_BTC", 20, 0.00095, "sell")

    # o = ybt_auth.open_orders("HEX_BTC")
    # print(o)
    # for i in o:
    #     ybt_auth.cancel_order(i["entrust_id"])
    # print(ybt_auth.order_detail("HEX_BTC", "1101002705978274"))
    # print(ybt_auth.cancel_order("HEX_BTC", "2101002719525705"))
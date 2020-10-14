from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hmac
import hashlib

import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class VinexAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def symbol_convert(self, symbol):
        symbol_pair = re.findall("[A-Z]+", symbol)
        symbol_base = symbol_pair[0]
        symbol_quote = symbol_pair[1]
        coin = symbol_quote + "_" + symbol_base
        return coin

    def get_server_time(self):
        url = self.urlbase + "time"
        response = requests.get(url)

        return response.json()["server_time"]

    def sign_message(self, data):
        try:
            return hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).hexdigest()
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
            with open(current_path + "/vinex_symbols_details.json", "r") as f:
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
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "place-order"
        timestamp = int(time.time())
        price_precision = ".8f"
        price = format(price, price_precision)

        order = dict()
        order['market'] = symbol
        order['amount'] = amount
        order['price'] = price
        order['type'] = side.upper()
        order['time_stamp'] = timestamp
        order["order_type"] = "LIMIT"
        order['recv_window'] = 60

        msg = ''
        for key in sorted(order.keys()):
            msg += '_' + str(order[key])
        msg = msg[1:]

        sign = self.sign_message(msg)
        header = {"api-key": self.apikey, 
                "signature": sign}
        response = requests.request("POST", url, data=order, headers=header)

        if response.json()["status"] == 200:
            return response.json()["data"]['uid']
        else:
            print(response.json()["message"])

    def cancel_order(self, symbol, entrust_id):
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "cancel-order"
        timestamp = int(time.time())

        order = dict()
        order['market'] = symbol
        order['time_stamp'] = timestamp
        order['uid'] = entrust_id
        order['recv_window'] = 60

        msg = ''
        for key in sorted(order.keys()):
            msg += '_' + str(order[key])
        msg = msg[1:]

        sign = self.sign_message(msg)
        header = {"api-key": self.apikey, 
                "signature": sign}
        response = requests.request("POST", url, data=order, headers=header)

        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": response.json()["message"]
        }
        print(info)

    def open_orders(self, symbol, status="OPENED"):
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "get-my-orders"
        timestamp = int(time.time())
        header = {"api-key": self.apikey}
        data = {"time_stamp": timestamp, 
                "market": symbol,
                "status": status,  # CANCELLED, FINISHED, ALL
                "limit": 100}
        response = requests.request("GET", url, data=data, headers=header)

        order_list = []
        try:
            for i in response.json()["data"]:
                if i["actionType"] == 0:
                    side = "sell"
                else:
                    side = "buy"
                order_list.append({
                    "symbol": i['pairSymbol'],
                    "entrust_id": i["uid"],
                    "price": i["price"],
                    "side": side,
                    "original_amount": i["amount"],
                    "remaining_amount": i["remain"],
                    "timestamp": i["createdAt"]
                })
            return order_list

        except Exception as e:
            print(e)

    def order_detail(self, symbol, id):
        order_list = self.open_orders(symbol, status="ALL")

        order_list = []
        try:
            for order in order_list:
                if id == order["entrust_id"]:
                    return order
            return None
        except Exception as e:
            print(e)

    def wallet_balance(self):
        url = self.urlbase + "balances"
        timestamp = int(time.time())
        header = {"api-key": self.apikey}
        data = {"time_stamp": timestamp}
        response = requests.request("GET", url, data=data, headers=header)
        results = []
        free, frozen = {} ,{}
        for coin in response.json()["data"]:
            if coin["free"] + coin["locked"] > 0:
                symbol = coin["asset"]
                free[symbol] = coin["free"]
                frozen[symbol] = coin["locked"]

        return free, frozen

if __name__ == "__main__":
    v_auth = VinexAuth("https://api.vinex.network/api/v2/", 
        "qsr0sp7sp8e786f4q5tt6t05nfnk3gnh", 
        "k9yiorvl5eoefi78oeqlpq0nqrrw6dr6")
    v_auth.place_order("BTC_ETH", 70586, 0.0000066, "buy")
    # print(v_auth.wallet_balance())
    # o = v_auth.open_orders("BTC_ETH")
    # for i in o:
    #     v_auth.cancel_order(i["entrust_id"])
    # print(v_auth.order_detail("dd3164b333a4afa9d5730bb87f6db8b3"))

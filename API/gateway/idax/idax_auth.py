from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hmac
import hashlib

# from key.idax_token import apl
import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class IdaxAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def get_server_time(self):
        url = self.urlbase + "time"
        response = requests.get(url)

        return response.json()["timestamp"]

    def sign_message(self, data):
        try:
            sorted_data = sorted(data.items(), key=lambda d: d[0], reverse=False)
            message = str(urlencode(sorted_data))
            return hmac.new(self.secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
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
            with open(current_path + "/idax_symbols_details.json", "r") as f:
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
            print (e)

    def get_price_precision(self, symbol):
        try:
            symbol_details = self.load_symbols_details()
            return int(symbol_details[symbol]["price_max_precision"])
        except Exception as e:
            print (e)

    def place_order(self, symbol, amount, price, side):
        url = self.urlbase + "placeOrder"
        timestamp = self.get_server_time()
        headers = {"Content-Type": "application/json"}
        amount_precision = self.get_amount_precision(symbol)
        amount_precision = "." + str(amount_precision) + "f"
        amount = format(amount, amount_precision)
        price_precision = self.get_price_precision(symbol)
        price_precision = "." + str(price_precision) + "f"
        price = format(price, price_precision)
        orderType = "limit"
        data = {"key": self.apikey, "pair": symbol, "orderType": orderType, "orderSide": side, "amount": str(amount), "price": str(price), "timestamp": timestamp}

        sign = self.sign_message(data)
        data["sign"] = sign
        data = json.dumps(data)

        is_ok, content = self.request("POST", url, data, headers)
        self.output("place_order", content)
        if is_ok:
            return content["orderId"]

    def cancel_order(self, entrust_id):
        url = self.urlbase + "cancelOrder"
        timestamp = self.get_server_time()
        headers = {"Content-Type": "application/json"}

        data = {"key": self.apikey, "orderId": entrust_id, "timestamp": timestamp}

        sign = self.sign_message(data)
        data["sign"] = sign
        data = json.dumps(data)

        is_ok, content = self.request("POST", url, data, headers)

        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": content
        }
        print(info)
        return is_ok

    def order_detail(self, symbol, entrust_id):
        url = self.urlbase + "orderInfo"
        timestamp = self.get_server_time()
        headers = {"Content-Type": "application/json"}
        pageIndex = 1
        pageSize = 1000

        data = {"key": self.apikey, "pair": symbol, "orderId": entrust_id, "pageIndex": pageIndex, "pageSize": pageSize, "timestamp": timestamp}

        sign = self.sign_message(data)
        data["sign"] = sign
        data = json.dumps(data)

        is_ok, content = self.request("POST", url, data, headers)

        if is_ok:
            order_list = []
            for i in content["orders"]:
                order_list.append({
                    "symbol": symbol,
                    "entrust_id": i["orderId"],
                    "price": i["price"],
                    "side": i["orderSide"],
                    "original_amount": i["quantity"],
                    "remaining_amount": float(i["quantity"]) - float(i["dealQuantity"]),
                    "timestamp": i["timestamp"]
                })
            if entrust_id != -1:
                return order_list[0]
            return order_list
        else:
            self.output("order_detail", content)

    def open_orders(self, symbol):
        try:
            return self.order_detail(symbol, -1)
        except Exception as e:
            print (e)

    def wallet_balance(self):
        url = self.urlbase + "userinfo"
        timestamp = self.get_server_time()
        headers = {"Content-Type": "application/json"}

        data = {"key": self.apikey, "timestamp": timestamp}
        sign = self.sign_message(data)
        data["sign"] = sign
        data = json.dumps(data)

        is_ok, content = self.request("POST", url, data, headers)
        # self.output("wallet_balance", content)
        if is_ok:
            return content["free"], content["freezed"]

if __name__ == "__main__":
    gny = {
        "api_key":
        "f9bd32416ed7470e951fa64c66c8dc6191e22f4dde3d42e08fd0703c6c2bf0e9",
        "api_secret":
        "dc66036c9d444236bfd1ddc987f4af1bdf2a610feba64a0d958b6105ab45c1ca"
    }

    ugc = {
    "api_key": "18990ddde7444548b82170f2baec62684b6d4c1bbe63416183de664aab3520df",
    "api_secret": "2e7a677be1c348feba11253889a7ee07ec29a50b92924eb2930f8204c4ed20d8"
    }
    idax = IdaxAuth("https://openapi.idax.pro/api/v2/", ugc["api_key"], ugc["api_secret"])
    # orderid1 = idax.place_order("UGC_BTC", 2.4, 0.0001382, "sell")
    # orderid2 = idax.place_order("UGC_BTC", 2.4, 0.0001382, "buy")
    # print(orderid1)
    # orderid2 = idax.place_order("APL_ETH", 145, 0.0000108, "buy")
    # print(idax.open_orders("APL_ETH"))
    # print(idax.order_detail("APL_ETH", orderid1))
    # print(idax.cancel_order(orderid1))
    # print(idax.cancel_order(orderid2))
    print(idax.wallet_balance())
    # print(idax.open_orders("APL_ETH"))
    # print(idax.order_detail("APL_ETH", orderid1))
    # print(idax.order_detail("APL_ETH", orderid2))
    # print(idax.in_order_list("APL_ETH"))
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hmac
import hashlib
import binascii
import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class ExratesAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def sign_message(self, method, endpoint, timestamp):
        try:
            payload = '|'.join([method, endpoint, str(timestamp), self.apikey])
            payload_encoded = payload.encode(encoding='UTF-8')
            signature = hmac.new(key=bytes(self.secret, encoding='UTF-8'), msg=payload_encoded, digestmod=hashlib.sha256).digest()
            sig_hex = binascii.hexlify(signature)
            return sig_hex.decode('UTF-8')
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
            with open(current_path + "/ex_auth_symbols_details.json", "r") as f:
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

    def place_order(self, symbol, amount, price, side):
        url = self.urlbase + "orders/create"
        timestamp = str(int(time.time() * 1000))

        sign = self.sign_message("POST", "/openapi/v1/orders/create", timestamp)

        headers = {"content-type": "application/json;charset=UTF-8",
                    "API-KEY": self.apikey, 
                    "API-TIME": timestamp, 
                    "API-SIGN": sign}

        data = {"currency_pair": symbol.lower(), 
                "order_type": side.upper(), 
                "amount": amount, 
                "price": price}
        data = json.dumps(data)
        is_ok, content = self.request("POST", url, data, headers)
        print(content)
        if is_ok:
            return content["created_order_id"]

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
        url = self.urlbase + "user/orders/open?currency_pair=%s" % symbol.lower()
        timestamp = str(int(time.time() * 1000))

        sign = self.sign_message("GET", "/openapi/v1/user/orders/open", timestamp)

        headers = {"Content-Type": "application/json",
                    "API-KEY": self.apikey, 
                    "API-TIME": timestamp, 
                    "API-SIGN": sign}

        is_ok, content = self.request("GET", url, "", headers)
        print(content)
        if is_ok:
            order_list = []
            for i in content:
                order_list.append({
                    "symbol": symbol,
                    "entrust_id": i["id"],
                    "price": i["price"],
                    "side": i["order_type"].lower(),
                    "original_amount": None,
                    "remaining_amount": float(i["amount"]),
                    "timestamp": i["date_created"]
                })
            return order_list
        else:
            self.output("open_orders", content)

    def wallet_balance(self):
        url = self.urlbase + "user/balances"
        timestamp = str(int(time.time() * 1000))

        sign = self.sign_message("GET", "/openapi/v1/user/balances", timestamp)

        headers = {"Content-Type": "application/json",
                    "API-KEY": self.apikey, 
                    "API-TIME": timestamp, 
                    "API-SIGN": sign}

        is_ok, content = self.request("GET", url, "", headers)
        # self.output("wallet_balance", content)
        free, frozen = {}, {}
        for coin in content:
            if float(coin["activeBalance"]) > 0 or float(coin["reservedBalance"]) > 0:
                free[coin["currencyName"]], frozen[coin["currencyName"]] = float(coin["activeBalance"]), float(coin["reservedBalance"])
        if is_ok:
            return free, frozen

if __name__ == "__main__":
    apl = {
        "api_key":
        "jfvhzXlCWCArEeXdaF6un0wyCDSkKGgFpHnDD8fu",
        "api_secret":
        "3GKMXn4u2MoRFZpdrTS26P2hg20nFplA4HHIJ0h2"
    }
    start = time.time()
    ex_auth = ExratesAuth("https://api.exrates.me/openapi/v1/", apl["api_key"], apl["api_secret"])
    # orderid1 = ex_auth.place_order("GNY_BTC", 187, 0.0000208, "sell")
    orderid2 = ex_auth.place_order("BTC_USD", 500, 1, "buy")
    # print(orderid2)
    # print(ex_auth.open_orders("APL_ETH"))
    # print(ex_auth.order_detail("APL_ETH", orderid1))
    # print(ex_auth.cancel_order(orderid1))
    # print(ex_auth.cancel_order(orderid2))
    # print(ex_auth.wallet_balance())
    # print(ex_auth.open_orders("BTC_USDT"))
    # print(ex_auth.order_detail("APL_ETH", orderid1))
    # print(ex_auth.order_detail("APL_ETH", orderid2))
    # print(ex_auth.in_order_list("APL_ETH"))
    end = time.time()
    print(end - start)
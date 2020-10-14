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
import base64
import math

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class CoinbaseAuth(object):
    def __init__(self, urlbase, key, secret, passphrase):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret
        self.passphrase = passphrase

    def symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))

    def sign_message(self, timestamp, method, path, data):
        try:
            # body = str(urlencode(data))
            message = timestamp + method.upper() + path + data
            message = message.encode('ascii')
            hmac_key = base64.b64decode(self.secret)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
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
            with open(current_path + "/coinbase_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            symbol_details = self.load_symbols_details()
            details = next(item for item in symbol_details if item["id"] == self.symbol_convert(symbol))
            return int(math.log10(1/float(details["base_increment"])))
        except Exception as e:
            print (e)

    def get_price_precision(self, symbol):
        try:
            symbol_details = self.load_symbols_details()
            details = next(item for item in symbol_details if item["id"] == self.symbol_convert(symbol))
            return int(math.log10(1/float(details["quote_increment"])))
        except Exception as e:
            print (e)

    def place_order(self, symbol, amount, price, side):
        url = self.urlbase + "orders"
        timestamp = str(time.time())

        price = format(price, '.'+str(self.get_price_precision(symbol)) + 'f')
        amount = format(amount, '.'+str(self.get_amount_precision(symbol)) + 'f')

        data = {
                "type": "limit",
                "size": amount,
                "price": price,
                "side": side,
                "product_id": self.symbol_convert(symbol)
        }
        data = json.dumps(data)
        sign = self.sign_message(timestamp, "POST", '/orders', data)
        headers = {
            "Content-Type": "Application/JSON", 
            "CB-ACCESS-KEY": self.apikey,
            "CB-ACCESS-SIGN": sign,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self.passphrase
            }
        
        is_ok, content = self.request("POST", url, data, headers)
        if is_ok:
            return content["id"]
        else:
            self.output("place_order", content)

    def cancel_order(self, entrust_id):
        url = self.urlbase + "orders/" + entrust_id
        timestamp = str(time.time())

        data = ""

        sign = self.sign_message(timestamp, "DELETE", "/orders/" + entrust_id, data)
        headers = {
            "Content-Type": "Application/JSON", 
            "CB-ACCESS-KEY": self.apikey,
            "CB-ACCESS-SIGN": sign,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self.passphrase
            }
        
        is_ok, content = self.request("DELETE", url, data, headers)
        if is_ok:
            return True
        else:
            self.output("cancel_order", content)

    def order_detail(self, entrust_id):
        url = self.urlbase + "orders/" + entrust_id
        timestamp = str(time.time())

        data = ""

        sign = self.sign_message(timestamp, "GET", "/orders/" + entrust_id, data)
        headers = {
                    "Content-Type": "Application/JSON", 
                    "CB-ACCESS-KEY": self.apikey,
                    "CB-ACCESS-SIGN": sign,
                    "CB-ACCESS-TIMESTAMP": timestamp,
                    "CB-ACCESS-PASSPHRASE": self.passphrase
                    }

        is_ok, content = self.request("GET", url, data, headers)

        if is_ok:
            return ({
                "symbol": '_'.join(content["product_id"].split('-')),
                "entrust_id": content["id"],
                "price": content["price"], 
                "side": content["side"],
                "original_amount": content["size"],
                "remaining_amount": float(content["size"]) - float(content["filled_size"]),
                "timestamp": time.mktime(time.strptime(content["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")) * 1000
            })
        else:
            self.output("order_detail", content)

    def open_orders(self, symbol):
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "orders"
        timestamp = str(time.time())

        data = {"product_id": symbol}
        data = json.dumps(data)

        sign = self.sign_message(timestamp, "GET", "/orders", data)
        headers = {
                    "Content-Type": "Application/JSON", 
                    "CB-ACCESS-KEY": self.apikey,
                    "CB-ACCESS-SIGN": sign,
                    "CB-ACCESS-TIMESTAMP": timestamp,
                    "CB-ACCESS-PASSPHRASE": self.passphrase
                    }

        is_ok, content = self.request("GET", url, data, headers)

        if is_ok:
            orders = []
            for i in content:
                orders.append({
                    "symbol": '_'.join(i["product_id"].split('-')),
                    "entrust_id": i["id"],
                    "price": i["price"], 
                    "side": i["side"],
                    "original_amount": i["size"],
                    "remaining_amount": float(i["size"]) - float(i["filled_size"]),
                    "timestamp": time.mktime(time.strptime(i["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")) * 1000
                })
            return orders
        else:
            self.output("order_detail", content)

    def wallet_balance(self):
        url = self.urlbase + "accounts"
        timestamp = str(time.time())

        data = ""
        sign = self.sign_message(timestamp, "GET", '/accounts', data)

        headers = {
            "Content-Type": "Application/JSON", 
            "CB-ACCESS-KEY": self.apikey,
            "CB-ACCESS-SIGN": sign,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self.passphrase
            }
        data = json.dumps(data)

        is_ok, content = self.request("GET", url, None, headers)

        if is_ok:
            free, frozen = {}, {}
            for coin in content:
                free[coin["currency"]] = float(coin["available"])
                frozen[coin["currency"]] = float(coin["hold"])
            return free, frozen
        else:
            self.output("wallet_balance", content)

if __name__ == "__main__":
    cb = {
        "api_key":
        "1",
        "api_secret":
        "2", 
        "passphrase": 
        "3"
    }

    cb_auth = CoinbaseAuth("https://api.pro.coinbase.com/", cb["api_key"], cb["api_secret"], cb["passphrase"])
    # orderid1 = cb_auth.place_order("ETH_USD", 0.1235466645, 153.333, "buy")
    # print (orderid1)
    # print(cb_auth.get_price_precision("ETH_USD"))
    # orderid2 = cb_auth.place_order("APL_ETH", 145, 0.0000108, "buy")
    # print(cb_auth.open_orders("BTC_USD"))
    # print(cb_auth.order_detail(orderid1))
    # print(cb_auth.cancel_order(orderid1))
    # print(cb_auth.cancel_order(orderid2))
    # print(cb_auth.wallet_balance())
    # print(cb_auth.open_orders("APL_ETH"))
    # print(cb_auth.order_detail("APL_ETH", orderid1))
    # print(cb_auth.order_detail("APL_ETH", orderid2))
    # print(cb_auth.in_order_list("APL_ETH"))
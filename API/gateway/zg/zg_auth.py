from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hashlib

from key.zg_token import znc
import random
import traceback
import six
import hmac

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class ZgAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret
        self.headers = headers = {#'Content-Type': 'application/x-www-form-urlencoded',
                                   'X-BH-APIKEY': self.apikey,
                                    'User-Agent': 'Broker-P V2.0.6'}

    def sign_message(self, data):
        try:
            params_str = urlencode(data)
            sign = hmac.new(self.secret.encode(encoding='UTF8'),
                          params_str.encode(encoding='UTF8'),
                          digestmod=hashlib.sha256).hexdigest()
            return sign
        except Exception as e:
            print (e)

    def request(self, method, url, data=None, headers=None):

        try:
            path = url + "?"
            for key in data.keys():
                if key != "signature":
                    path += key + "=" + str(data[key]) + "&"
            path = path + "signature=" + str(data["signature"])
            data = json.dumps(data)
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
                print(error)
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

    def symbol_convert(self, symbol):
        return ''.join(symbol.split('_')) 
        
    def output(self, function_name, content):
        info = {
            "func_name": function_name,
            "response": content
        }
        print (info)

    def place_order(self, symbol, amount, price, side):
        try:
            zg_symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/openapi/v1/order"
            params=dict()
            params["symbol"] = zg_symbol
            params["side"] = side.upper()
            params["type"] = "LIMIT"
            params["timeInForce"] = "GTC"
            params["quantity"] = amount
            params["price"] = price
            params["recvWindow"] = 5000
            params["timestamp"] = int(time.time() * 1000)

            params['signature'] = self.sign_message(params)

            is_ok, content = self.request("POST", url, params, self.headers)
            if is_ok:
                return content["orderId"]
            else:
                self.output("place order", content)
        except Exception as e:
            print (e)

    def cancel_order(self, symbol, entrust_id):
        try:
            url = self.urlbase + "/openapi/v1/order"
            params=dict()
            params["orderId"] = entrust_id
            params["recvWindow"] = 5000
            params["timestamp"] = int(time.time() * 1000)

            params['signature'] = self.sign_message(params)

            is_ok, content = self.request("DELETE", url, params, self.headers)
            if "symbol" in content.keys():
                is_ok = True
            else:
                is_ok = False
            info = {
                "func_name": 'cancel_order',
                "entrust_id": entrust_id,
                "response": content
            }
            print(info)
            return is_ok
        except Exception as e:
            print (e)

    def order_detail(self, symbol, entrust_id):
        try:
            url = self.urlbase + "/openapi/v1/order"
            params=dict()
            params["orderId"] = entrust_id
            params["recvWindow"] = 5000
            params["timestamp"] = int(time.time() * 1000)

            params['signature'] = self.sign_message(params)
            is_ok, content = self.request("GET", url, params, self.headers)
            
            if is_ok:
                if symbol == content["symbol"]:
                    order_detail = {
                            "symbol": symbol,
                            "entrust_id": content["orderId"],
                            "price": content["price"],
                            "side": content["side"].lower(),
                            "original_amount": float(content["origQty"]),
                            "remaining_amount": float(content["origQty"]) - float(content["executedQty"]),
                            "timestamp": content["time"]
                            }

                return order_detail
            else:
                self.output("order detail", content)
        except Exception as e:
            print (e)

    def open_orders(self, symbol):
        try:
            zg_symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/openapi/v1/openOrders"
            params=dict()
            params["symbol"] = zg_symbol
            params["recvWindow"] = 5000
            params["timestamp"] = int(time.time()) * 1000

            params['signature'] = self.sign_message(params)
            is_ok, content = self.request("GET", url, params, self.headers)
            if is_ok:
                order_list = []
                for i in content:
                    order_list.append({
                        "symbol": symbol,
                        "entrust_id": i["orderId"],
                        "price": i["price"],
                        "side": i["side"].lower(),
                        "original_amount": float(i["origQty"]),
                        "remaining_amount": float(i["origQty"]) - float(i["executedQty"]),
                        "timestamp": i["time"]
                        })
                return order_list
            else:
                self.output("open orders", content)
        except Exception as e:
            print (e)

    def wallet_balance(self):
        try:
            url = self.urlbase + "/openapi/v1/account"
            params=dict()
            params["recvWindow"] = 5000
            params["timestamp"] = str(int(time.time() * 1000))

            params['signature'] = self.sign_message(params)
            is_ok, content = self.request("GET", url, params, self.headers)
            if is_ok:
                free, frozen = {}, {}
                if "balances" in content.keys():
                    for fund in content["balances"]:
                        coin = fund["asset"]
                        free[coin] = fund["free"]
                        frozen[coin] = fund["locked"]
                return free, frozen
            else:
                self.output("wallet balance", content)
        except Exception as e:
            print (e)

if __name__ == "__main__":
    api_key=""
    api_secret=""
    
    zg = ZgAuth("https://api.zg8.com", api_key, api_secret)
    # free, frozen = zg.wallet_balance()
    # print(free)
    # orderid1 = zg.place_order("ETH_USDT", 1, 150, "buy")
    # orderid2 = zg.place_order("ZNC_USDT", 5000, 0.000490, "sell")
    # print(orderid1)
    # print(orderid2)
    # orderid2 = zg.place_order("APL_ETH", 145, 0.0000108, "buy")
    # ods = zg.open_orders("ZNC_USDT")
    # for o in ods:
    #     print(o["side"], o["entrust_id"], o["price"], o["remaining_amount"])
    #     if float(o["remaining_amount"]) >= 20000.0:
    #         print(zg.cancel_order(o["entrust_id"]))
    # time.sleep(2)
    # print(zg.order_detail("ZNC_USDT", orderid1))
    # print(zg.cancel_order(orderid1))
    # print(zg.cancel_order(orderid2))
    # print(zg.cancel_order("7a421a98a8564515b7e3bda43780871e"))
    # print(zg.wallet_balance())
    # print(zg.open_orders("APL_ETH"))
    # print(zg.order_detail("APL_ETH", orderid1))
    # print(zg.order_detail("APL_ETH", orderid2))
    # print(zg.in_order_list("APL_ETH"))
    # open_orders = zg.open_orders("ETH_USDT")
    # print(open_orders)
    # print(zg.cancel_order("ETH_USDT",645613032568893440))

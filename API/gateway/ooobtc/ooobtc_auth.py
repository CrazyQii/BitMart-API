from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hmac
import hashlib
from constant.base_url import ooobtc_base_url

from key.ooobtc_token import lpk
import random
import traceback
from urllib import urlencode

class OoobtcAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

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

    def sign(self, data):
        sign = hmac.new(self.secret, data, hashlib.sha1).hexdigest()
        
        return sign

    def place_order(self, symbol, amount, price, side):
        amount = format(amount, ".10f")
        price = format(price, ".10f")
        params = {"action": side, "price": price, "number": amount, "coin": symbol.lower()}
        data = json.dumps(params)

        sign = self.sign(data)

        headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Content-Type':'application/json',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',

            'timestamp':str(int(time.time())),
            'sign':sign,
            'access-key':self.apikey,
        }

        url = self.urlbase + "private/v1/trade"
        is_ok, content = self.request("POST", url, data, headers)
        self.output("place_order", content)

        # if is_ok:
            # return content["clientOrderId"]

    def cancel_order(self, entrust_id):
        params = {"action": "cancel", "id": entrust_id}
        data = json.dumps(params)

        sign = self.sign(data)

        headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Content-Type':'application/json',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',

            'timestamp':str(int(time.time())),
            'sign':sign,
            'access-key':self.apikey,
        }

        url = self.urlbase + "private/v1/cancel"
        is_ok, content = self.request("POST", url, data, headers)
        print content

        if is_ok:
            print ("cancel order success.")
        else:
            self.output("cancel_order", content)

        return is_ok

    def cancel_all(self, symbol):
        orders = self.open_orders(symbol)
        for i in orders:
            self.cancel_order(i["entrust_id"])

    def order_detail(self, symbol, entrust_id):
        orders = self.open_orders(symbol)
        
        return [i for i in orders if i["entrust_id"] == entrust_id]

    def open_orders(self, symbol):
        params = {"action": "myorders", "coin": symbol}
        data = json.dumps(params)

        sign = self.sign(data)

        headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Content-Type':'application/json',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',

            'timestamp':str(int(time.time())),
            'sign':sign,
            'access-key':self.apikey,
        }

        url = self.urlbase + "private/v1/myorders"
        is_ok, content = self.request("POST", url, data, headers)
        
        if is_ok:
            order_list = []
            for i in content["data"]:
                order_list.append({
                    "symbol": symbol,
                    "price": float(i["price"]),
                    "status": "",
                    "timestamp": int(i["created"]),
                    "side": i["flag"],
                    "remaining_amount": float(i["numberover"]),
                    "original_amount": float(i["number"]),
                    "entrust_id": i["id"]
                })
            return order_list
        else:
            self.output("open_orders", content)

    def wallet_balance(self):
        params = {"action": "cancel"}
        data = json.dumps(params)

        sign = self.sign(data)

        headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Content-Type':'application/json',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',

            'timestamp':str(int(time.time())),
            'sign':sign,
            'access-key':self.apikey,
        }

        url = self.urlbase + "private/v1/getbalance"
        is_ok, content = self.request("GET", url, data, headers)

        if is_ok:
            free, frozen = {}, {}
            for coin in content["data"].keys():
                free[coin] = content["data"][coin]["avaliable"]
                frozen[coin] = content["data"][coin]["lock"]
            return free, frozen


if __name__ == "__main__":
    ooobtc_auth = OoobtcAuth(ooobtc_base_url, lpk["api_key"], lpk["api_secret"])
    # orderid1 = ooobtc_auth.place_order("CST_BTC", 10000, 0.00000056, "buy")
    # orderid2 = ooobtc_auth.place_order("LPK_ETH", 100, 0.00007, "sell")
    # orderid3= ooobtc_auth.place_order("AE_ETH", 3, 0.003, "buy")
    # print ooobtc_auth.order_detail("AE_ETH", "61259444")
    # print ooobtc_auth.order_detail("LPK_ETH", orderid3)
    # print ooobtc_auth.cancel_order("61258253")
    # print ooobtc_auth.open_orders("AE_ETH")
    # print ooobtc_auth.cancel_all("AE_ETH")
    # print ooobtc_auth.wallet_balance()

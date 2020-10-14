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
import string
import random
import traceback
import hmac

from requests import get


class LbankAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def sign_message(self, params, timestamp):
        p = params
        p[ "timestamp" ] = timestamp
        p[ "signature_method" ] = 'HmacSHA256'
        par = [ ]
        for k in sorted( p.keys() ):
            par.append( k + '=' + str( p[ k ] ) )
        par = '&'.join( par )
        msg = hashlib.md5( par.encode( "utf8" ) ).hexdigest().upper()

        appsecret = bytes(self.secret, encoding='utf8' )
        data=bytes(msg,encoding='utf8')
        signature=hmac.new(appsecret,data,digestmod=hashlib.sha256).hexdigest().lower()

        return signature

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
            with open(current_path + "/lbank_symbols_details.json", "r") as f:
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
        price_precision = ".6f"
        price = format(price, price_precision)

        num = string.ascii_letters + string.digits
        randomstr = "".join(random.sample(num, 35))

        t = str(time.time() * 1000 ).split( "." )[ 0 ]

        header = {"Accept-Language": 'zh-CN', "signature_method":"HmacSHA256", 'timestamp': t, 'echostr': randomstr}
        par = {}
        par["api_key"] = self.apikey
        par["symbol"] = symbol.lower()
        par["type"] = side.lower()
        par["price"] = price
        par["amount"] = amount
        par["echostr"] = randomstr
        sign=self.sign_message(par, t)

        url = self.urlbase + "v2/create_order.do"

        par["sign"] = sign
        del par["signature_method"]
        del par["timestamp"]
        del par["echostr"]
        response = requests.request("POST", url, data=par, headers=header)
        if response.json()["result"]:
            return response.json()["data"]["order_id"]

    def cancel_order(self, symbol, entrust_id):
        num = string.ascii_letters + string.digits
        randomstr = "".join(random.sample(num, 35))

        t = str(time.time() * 1000 ).split( "." )[ 0 ]

        header = {"Accept-Language": 'zh-CN', "signature_method":"HmacSHA256", 'timestamp': t, 'echostr': randomstr}
        par = {}
        par["api_key"] = self.apikey
        par["symbol"] = symbol.lower()
        par["order_id"] = entrust_id
        par["echostr"] = randomstr
        sign=self.sign_message(par, t)

        url = self.urlbase + "v2/cancel_order.do"

        par["sign"] = sign
        del par["signature_method"]
        del par["timestamp"]
        del par["echostr"]
        response = requests.request("POST", url, data=par, headers=header)
        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": response.json()
        }
        print(info)

    def open_orders(self, symbol):
        num = string.ascii_letters + string.digits
        randomstr = "".join(random.sample(num, 35))

        t = str(time.time() * 1000 ).split( "." )[ 0 ]

        header = {"Accept-Language": 'zh-CN', "signature_method":"HmacSHA256", 'timestamp': t, 'echostr': randomstr}
        par = {}
        par["api_key"] = self.apikey
        par["symbol"] = symbol.lower()
        par["current_page"] = 1
        par["page_length"] = 200
        par["echostr"] = randomstr
        sign=self.sign_message(par, t)

        url = self.urlbase + "v2/orders_info_no_deal.do"

        par["sign"] = sign
        del par["signature_method"]
        del par["timestamp"]
        del par["echostr"]
        response = requests.request("POST", url, data=par, headers=header)
        order_list = []
        try:
            for i in response.json()["data"]["orders"]:
                order_list.append({
                    "symbol": symbol,
                    "entrust_id": i["order_id"],
                    "price": i["price"],
                    "side": i["type"],
                    "original_amount": i["amount"],
                    "remaining_amount": float(i["amount"]) - float(i["deal_amount"]),
                    "timestamp": int(i["create_time"])
                })
            return order_list

        except Exception as e:
            print(e)

    def order_detail(self, symbol, entrustId):
        num = string.ascii_letters + string.digits
        randomstr = "".join(random.sample(num, 35))

        t = str(time.time() * 1000 ).split( "." )[ 0 ]

        header = {"Accept-Language": 'zh-CN', "signature_method":"HmacSHA256", 'timestamp': t, 'echostr': randomstr}
        par = {}
        par["api_key"] = self.apikey
        par["symbol"] = symbol.lower()
        par["order_id"] = entrustId
        par["echostr"] = randomstr
        sign=self.sign_message(par, t)

        url = self.urlbase + "v2/orders_info.do"

        par["sign"] = sign
        del par["signature_method"]
        del par["timestamp"]
        del par["echostr"]
        response = requests.request("POST", url, data=par, headers=header)
        try:
            order = response.json()["data"][0]
            return ({
                "symbol": symbol,
                "entrust_id": entrustId,
                "price": order["price"],
                "side": order["type"],
                "original_amount": order["amount"],
                "remaining_amount": float(order["amount"]) - float(order["deal_amount"]),
                "timestamp": order["create_time"]
            })
        except Exception as e:
            print(e)

    def wallet_balance(self):
        num = string.ascii_letters + string.digits
        randomstr = "".join(random.sample(num, 35))

        t = str(time.time() * 1000 ).split( "." )[ 0 ]

        header = {"Accept-Language": 'zh-CN', "signature_method":"HmacSHA256", 'timestamp': t, 'echostr': randomstr}
        par = {}
        par["api_key"]=self.apikey
        par[ 'echostr' ] = randomstr
        sign=self.sign_message(par, t)

        url = self.urlbase + "v2/user_info.do"

        par[ 'sign' ] = sign
        del par["signature_method"]
        del par["timestamp"]
        del par['echostr']
        response = requests.request("POST", url, data=par, headers=header)
        balances = response.json()["data"]
        results = []
        free, frozen = {} ,{}
        for coin in balances["free"].keys():
            if float(balances["free"][coin]) + float(balances["freeze"][coin]) > 0:
                symbol = coin.upper()
                free[symbol] = balances["free"][coin]
                frozen[symbol] = balances["freeze"][coin]
        return free, frozen

if __name__ == "__main__":
    lb_auth = LbankAuth("https://api.lbkex.com/", 
        "1d013f60-6737-4dd6-9cf9-bc34b080e8a4", 
        "DBF09C4E3BDB2E25940566BA195D56FD")
    # print(lb_auth.place_order("HEX_USDT", 1000, 0.0045, "buy"))
    # ip = get('https://api.ipify.org').text
    # print(ip)

    # print(lb_auth.wallet_balance())
    # order1 = lb_auth.place_order("HEX_USDT", 100, 0.003, "buy")
    # order2 = lb_auth.place_order("HEX_USDT", 20, 0.00095, "sell")

    # o = lb_auth.open_orders("HEX_USDT")
    # print(o)
    # for i in o:
    #     if random.random() < 0.5:
    # order1 = "fd8e8494-27e8-4d2f-a07d-89d143488d65"
    #         lb_auth.cancel_order("HEX_SXC", i["entrust_id"])
    # print(lb_auth.order_detail("HEX_USDT", order1))
    # print(lb_auth.cancel_order("HEX_USDT", order1))

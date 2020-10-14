import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hashlib

import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class XtAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def sign_message(self, data):
        try:
            return hashlib.md5(data.encode()).hexdigest()
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
        url = "https://www.xt.com/exchange/entrust/controller/website/EntrustController/addEntrust"
        timestamp = int(time.time() * 1000)
        price_precision = ".6f"
        price = format(price, price_precision)

        symbols_details = self.load_symbols_details()

        order = dict()
        order['marketId'] = symbols_details[symbol]["marketId"]
        order['amount'] = str(int(amount))
        order['price'] = price
        order['type'] = "0" if side == "sell" else "1"
        order['rangeType'] = "0"
        order_json = json.dumps(order, separators=(',', ':'))

        msg = self.apikey + str(timestamp) + str(order_json) + self.secret
        sign = self.sign_message(msg)
        header = {"Apiid": self.apikey, 
                    "Timestamp": str(timestamp), 
                    "Clienttype": "5", 
                    "Sign": sign, 
                    "Content-type": "application/json"}
        response = requests.request("POST", url, data=order_json, headers=header)

        if response.json()["resMsg"]["code"] == "1":
            print("here")
            return response.json()["datas"]['entrustId']
        else:
            print(response.json()["resMsg"]["message"])

    def cancel_order(self, symbol, entrust_id):
        url = "https://www.xt.com/exchange/entrust/controller/website/EntrustController/cancelEntrust"
        
        symbols_details = self.load_symbols_details()
        symbol_id = symbols_details[symbol]["marketId"]
        timestamp = int(time.time() * 1000)

        order = {"entrustId": entrust_id,
                 "marketId": symbol_id}
        order_json = json.dumps(order, separators=(',', ':'))

        msg = self.apikey + str(timestamp) + str(order_json) + self.secret
        sign = self.sign_message(msg)

        header = {"Apiid": self.apikey, 
                    "Timestamp": str(timestamp), 
                    "Clienttype": "5", 
                    "Sign": sign, 
                    "Content-type": "application/json"}
        response = requests.request("POST", url, data=order_json, headers=header)

        info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": response.json()["resMsg"]
        }
        print(info)

    def open_orders(self, symbol):
        symbols_details = self.load_symbols_details()
        symbol_id = symbols_details[symbol]["marketId"]

        url = "https://www.xt.com/exchange/entrust/controller/website/EntrustController/getUserEntrustRecordFromCacheWithPage?marketId=%s&pageSize=100" % symbol_id
        
        timestamp = int(time.time() * 1000)
        msg = self.apikey + str(timestamp) + "marketId" + symbol_id + "pageSize100" + self.secret
        sign = self.sign_message(msg)

        header = {"Apiid": self.apikey, 
                    "Timestamp": str(timestamp), 
                    "Clienttype": "5", 
                    "Sign": sign}
        
        response = requests.request("GET", url, headers=header)

        order_list = []
        try:
            for i in response.json()["datas"]["entrustList"]:
                if str(i["type"]) == "0":
                    side = "sell"
                elif str(i["type"]) == "1":
                    side = "buy"
                elif str(i["type"]) == "-1":
                    side = "cancelled"
                order_list.append({
                    "symbol": symbol,
                    "entrust_id": i["entrustId"],
                    "price": i["price"],
                    "side": side,
                    "original_amount": i["amount"],
                    "remaining_amount": float(i["amount"]) - float(i["completeAmount"]),
                    "timestamp": int(i["createTime"]/1000)
                })
            return order_list

        except Exception as e:
            print(e)

    def order_detail(self, symbol, entrustId):
        symbols_details = self.load_symbols_details()
        symbol_id = symbols_details[symbol]["marketId"]

        url = "https://www.xt.com/exchange/entrust/controller/website/EntrustController/getEntrustById?marketId=%s&entrustId=%s" % (symbol_id, entrustId)

        timestamp = int(time.time() * 1000)
        msg = self.apikey + str(timestamp) + "entrustId" + str(entrustId) + "marketId" + symbol_id + self.secret
        sign = self.sign_message(msg)

        header = {"Apiid": self.apikey, 
                    "Timestamp": str(timestamp), 
                    "Clienttype": "5", 
                    "Sign": sign}
        
        response = requests.request("GET", url, headers=header)

        try:
            order = response.json()["datas"]
            if str(order["type"]) == "0":
                side = "sell"
            elif str(order["type"]) == "1":
                side = "buy"
            elif str(order["type"]) == "-1":
                side = "cancelled"
            return ({
                "symbol": symbol,
                "entrust_id": entrustId,
                "price": order["price"],
                "side": side,
                "original_amount": order["amount"],
                "remaining_amount": float(order["amount"]) - float(order["completeAmount"]),
                "timestamp": order["createTime"]
            })
        except Exception as e:
            print(e)

    def load_currency_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            currency_details = {}
            with open(current_path + "/xt_currency_details.json", "rb") as f:
                currency_details = json.load(f)
            f.close()
            return currency_details
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/xt_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def wallet_balance(self):
        url = "https://www.xt.com/exchange/fund/controller/website/FundController/findByPage"
        timestamp = int(time.time() * 1000)
        sign = self.sign_message(self.apikey + str(timestamp) + self.secret)
        header = {"Apiid": self.apikey, 
                    "Timestamp": str(timestamp), 
                    "Clienttype": "5", 
                    "Sign": sign}
        response = requests.request("GET", url, headers=header)
        results = []
        free, frozen = {} ,{}
        currency = self.load_currency_details()
        for coin in response.json()["datas"]["list"]:
            if float(coin["amount"]) + float(coin["freeze"]) > 0:
                coin_name = None
                for item in currency:
                    if str(item["currencyId"]) == str(coin["currencyTypeId"]):
                        coin_name = item["name"].upper()
                        break
                symbol = coin_name
                free[symbol] = coin["amount"]
                frozen[symbol] = coin["freeze"]
        return free, frozen

if __name__ == "__main__":
    xt_auth = XtAuth("", 
        "7vUUPcndlrM7vUUPcndlrN", 
        "cb5ef1bbbe220155b08fb3e2bc583bda")
    # print(xt_auth.place_order("HEX_USDT", 1, 0.0005, "buy"))
    # print(xt_auth.wallet_balance())
    # order1 = xt_auth.place_order("HEX_USDT", 20, 0.00095, "buy")
    # order2 = xt_auth.place_order("HEX_USDT", 20, 0.00095, "sell")

    # o = xt_auth.open_orders("HEX_SXC")
    # print(o)
    # for i in o:
    #     xt_auth.cancel_order(i["entrust_id"])
    # print(xt_auth.order_detail("HEX_SXC", "E6653227871655538688"))
    # print(xt_auth.cancel_order("HEX_USDT", "E6653415791632953344"))
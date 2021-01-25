from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import re
import requests
import time
import hashlib
from Gateway.base_url import coinzeus_base_url

from key.coinzeus_token import wpc
import traceback


class CoinzeusAuth(object):
    def __init__(self, urlbase, api_key, api_secret, login_name):
        self.urlbase = urlbase
        self.apikey = api_key
        self.secret = api_secret
        self.login_name = login_name

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "/" + symbol_quote
        except Exception, e:
            print e

    def side_convert(self, side):
        try:
            if side == "sell":
                return ("ask")
            elif side == "buy":
                return ("bid")
            else:
                return side
        except Exception, e:
            print e

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

    # can also show how much is being withdrawn
    def get_balance(self):
        url = self.urlbase + "api/account/balance"
        data = {"mbId": self.login_name, "apiKey": self.apikey}
        
        msg = self.apikey + self.login_name + self.secret
        sign = hashlib.sha256(msg.encode()).hexdigest()
        headers = {"SecretHeader": sign}

        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            return response["data"]["avail"], response["data"]["in_use"] #, response["data"]["total"], response["data"]["in_withdraw"]
        else:
            print ("Error: get_balance() error. response:", response)

    # @params
    # side: ask, bid
    def place_order(self, symbol, amount, price, side):
        url = self.urlbase + "api/trade/orderPlace"
        side = self.side_convert(side)
        amount = format(amount, ".10f")
        price = format(price, ".10f")
        symbol = self.symbol_convert(symbol)
        data = {
            "mbId": self.login_name,
            "pairName": symbol,
            "action": side,
            "price": price,
            "amount": amount,
            "apiKey": self.apikey
            }
            
        msg = self.apikey + self.login_name + symbol + side + str(price) + str(amount) + self.secret
        sign = hashlib.sha256(msg.encode()).hexdigest()
        headers = {"SecretHeader": sign}
            
        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            return response["data"]
        else:
            print("Error: place_order() error. response:", response)

    def cancel_order(self, symbol, order_id, price, side):
        url = self.urlbase + "api/trade/orderCancel"
        side = self.side_convert(side)
        price = format(float(price), ".10f")
        symbol = self.symbol_convert(symbol)
        data = {
            "mbId": self.login_name,
            "pairName": symbol,
            "ordNo": order_id,
            "action": side,
            "ordPrice": price,
            "apiKey": self.apikey}
            
        msg = self.apikey + self.login_name + symbol + str(order_id) + side + str(price) + self.secret
        sign = hashlib.sha256(msg.encode()).hexdigest()
        headers = {"SecretHeader": sign}

        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            return response
        else:
            print ("Error: calcel_order() error. response:", response)

    def cancel_all(self, symbol):
        try:
            open_orders = self.open_orders("WPC_BTC")
            print open_orders
            for i in open_orders:
                print self.cancel_order(symbol, i["entrust_id"], i["price"], i["side"])

        except Exception, e:
            print e

    def open_orders(self, symbol):
        url = self.urlbase + "api/account/openOrders"
        underline_symbol = symbol
        symbol = self.symbol_convert(symbol)
        data = {
            "mbId": self.login_name,
            "pairName": symbol,
            "action": "all",
            "cnt": 200,
            "skipIdx": 0,
            "apiKey": self.apikey
            }
            
        msg = self.apikey + self.login_name + symbol + "all" + "200" + "0" + self.secret
        sign = hashlib.sha256(msg.encode()).hexdigest()
        headers = {"SecretHeader": sign}
            
        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            open_orders = []
            for i in response["data"]["list"]:
                side = "buy"
                if i["action"] == "ask":
                    side = "sell"
                open_orders.append({
                    "symbol": underline_symbol,
                    "entrust_id": i["ordNo"],
                    "price": i["ordPrice"],
                    "side": side,
                    "original_amount": i["ordAmount"],
                    "remaining_amount": i["remainAmount"],
                    "timestamp": int(time.mktime(time.strptime(i["ordDt"], "%Y%m%d%H%M%S")))
                })
            return open_orders
        else:
            print ("Error: open_orders() error. response:", response)

if __name__ == "__main__":
    coinzeus_auth = CoinzeusAuth(coinzeus_base_url, wpc["api_key"], wpc["api_secret"], wpc["login_name"])
    # print coinzeus_auth.get_balance()
    # print coinzeus_auth.place_order("WPC_BTC", 1277, 0.00000505, "buy")
    # print coinzeus_auth.place_order("WPC_BTC", 127, 0.00000568, "sell")
    # print coinzeus_auth.cancel_order("WPC_BTC", 19030842261, 0.00000568, "sell")


    # a = coinzeus_auth.open_orders("WPC_BTC")
    # print a
    # for i in a:
        # print coinzeus_auth.cancel_order("WPC_BTC", (i["entrust_id"]), (i["price"]), i["side"])
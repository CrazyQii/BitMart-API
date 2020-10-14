from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import re
import requests
import time
import hashlib
import hmac
import random
import traceback

try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


class GateioAuth(object):
    def __init__(self, urlbase, key, secret):
        self.apikey = key
        self.urlbase = urlbase
        self.secret = secret

    def sign_message(self, params):
        try:
            bSecretKey = bytes(self.secret, encoding='utf8')
            sign = ''

            for key in params.keys():
                value = str(params[key])
                sign += key + '=' + value + '&'
                
            bSign = bytes(sign[:-1], encoding='utf8')
            mySign = hmac.new(bSecretKey, bSign, hashlib.sha512).hexdigest()
            return mySign
        except Exception as e:
            print (e)

    def load_symbols_details(self):
        try:
            current_path = path.dirname(path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/gateio_markets_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    # def get_amount_precision(self, symbol):
        # try:
            # symbol_details = self.load_symbols_details()
            # for details in symbol_details:
                # if details["id"] == symbol:
                    # return int(symbol_details[symbol]["quantityScale"])
        # except Exception as e:
            # print (e)

    def place_order(self, symbol, amount, price, side):
        params = {'currencyPair': symbol.lower(),
                  'rate': str(price),
                  'amount': str(amount)}
        headers = {
                    "Content-type" : "application/x-www-form-urlencoded",
                    "KEY": self.apikey, 
                    'SIGN': self.sign_message(params)
                    }
        # url = self.urlbase + 'private/order'
        if side == "buy":
            url = "https://api.gateio.co/api2/1/private/buy"
        else:
            url = "https://api.gateio.co/api2/1/private/sell"
        response = requests.request('POST', url, data=params, headers=headers)
        return response.json()["orderNumber"]

    def cancel_order(self, symbol, entrust_id):
        # url = self.urlbase + "cancelOrder"
        url = "https://api.gateio.co/api2/1/private/cancelOrder"
        # timestamp = self.get_server_time()
        
        params = {'currencyPair': symbol.lower(),
                  'orderNumber': entrust_id}
        headers = {
                    "Content-type" : "application/x-www-form-urlencoded",
                    "KEY": self.apikey, 
                    'SIGN': self.sign_message(params)
                    }

        response = requests.request('POST', url, data=params, headers=headers)
        return response.json()["result"]

    def order_detail(self, symbol, entrust_id):
        # url = self.urlbase + "orderInfo"
        # timestamp = self.get_server_time()
        url = "https://api.gateio.co/api2/1/private/getOrder"
        params = {'currencyPair': symbol.lower(),
                  'orderNumber': entrust_id}
        headers = {
                    "Content-type" : "application/x-www-form-urlencoded",
                    "KEY": self.apikey, 
                    'SIGN': self.sign_message(params)
                    }

        response = requests.request('POST', url, data=params, headers=headers).json()
        is_ok = response["result"]
        if is_ok:
            return ({
                "symbol": symbol,
                "entrust_id": entrust_id,
                "price": response["order"]["rate"],
                "side": response["order"]["type"],
                "original_amount": response["order"]["initialAmount"],
                "remaining_amount": response["order"]["amount"],
                "timestamp": None
            })
        else:
            self.output("order_detail", response)
            
    def open_orders(self, symbol):
        # url = self.urlbase + "orderHistory"
        # timestamp = self.get_server_time()
        url = "https://api.gateio.co/api2/1/private/openOrders"
        params = {'currencyPair': symbol.lower()}
        headers = {
                    "Content-type" : "application/x-www-form-urlencoded",
                    "KEY": self.apikey, 
                    'SIGN': self.sign_message(params)
                    }

        response = requests.request('POST', url, data=params, headers=headers).json()
        is_ok = response["result"]

        if is_ok:
            order_list = []
            for o in response["orders"]:
                order_list.append({
                    "symbol": symbol,
                    "entrust_id": o["orderNumber"],
                    "price": o["rate"],
                    "side": o["type"],
                    "original_amount": o["initialAmount"],
                    "remaining_amount": o["amount"],
                    "timestamp": o["timestamp"]
            })
            return order_list
        else:
            self.output("open_orders", content)

    def wallet_balance(self):
        try:
            # url = self.urlbase + "spot/accounts"
            url = "https://api.gateio.co/api2/1/private/balances"
            params = {}            
            headers = {
                        "Content-type" : "application/x-www-form-urlencoded",
                        "KEY": self.apikey, 
                        'SIGN': self.sign_message(params)
                        }
            response = requests.request('POST', url, params=params, headers=headers)
            balances = response.json()
            return balances["available"], balances["locked"]
        except Exception as e:
            print(e)
            
            
if __name__ == "__main__":
    yaofund = {
    "api_key":
    "02EA39FC-E922-41A4-BDFB-3136E10C0520",
    "api_secret":
    "7f471183d70749e1a6e5ce8162eafb31c71a4ec0e03687f0ed64c93249945a20"
    }

    gate_auth = GateioAuth("https://api.gateio.ws/api/v4/", yaofund["api_key"], yaofund["api_secret"])
    # orderid1 = gate_auth.place_order('etc_btc', '123', '0.001', "sell")
    # print(orderid1)
    # orderid2 = gate_auth.place_order("APL_ETH", 145, 0.0000108, "buy")
    # print(gate_auth.open_orders("APL_ETH"))
    # print(gate_auth.order_detail("APL_ETH", orderid1))
    # print(gate_auth.cancel_order(orderid1))
    # print(gate_auth.cancel_order("BTC_USDT", 12456416516))
    # print(gate_auth.cancel_order(orderid2))
    # print(gate_auth.wallet_balance())
    # print(gate_auth.open_orders("APL_ETH"))
    # print(gate_auth.order_detail("APL_ETH", orderid1))
    # print(gate_auth.order_detail("APL_ETH", orderid2))
    # print(gate_auth.in_order_list("APL_ETH"))
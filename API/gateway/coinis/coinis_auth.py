import requests
from coinis_public import CoinisPublic
from coinis_token_access import access_token
import re
import json

class CoinisAuth(object):
    def __init__(self, urlbase, token, accno, accpwd):
        self.urlbase = urlbase
        self.token = token
        self.accno = accno
        self.accpwd = accpwd
        self.coinis_public = CoinisPublic(urlbase)

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        try:
            symbol = self.symbol_convert(symbol)
            headers = {"Content-type": "application/json", "x-access-token": self.token}
            url = self.urlbase
            if side == "buy":
                url += "trade/buy"
            if side == "sell":
                url += "trade/sell"
            data = {"accno": self.accno, "accpwd": self.accpwd, "itemcode": symbol, "ordertype": "price", "price": price, "amount": amount}
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            # print response.content
            if response.json()["result"] == -7359:
                print("ERROR! Minimum order amount or server error.")
            return response.json()["data"]

        except Exception as e:
            print("ERROR! Minimum order amount or server error.")
            print(e)

    def wallet_balance(self, coin_type):
        try:
            headers = {"Content-type": "application/json", "x-access-token": self.token}
            url = self.urlbase + "wallet/balance"
            data = {"accno": self.accno, "acctype": coin_type}
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            # print(response.content)
            return float(response.json()["data"]["coinWithdrawBalance"]), float(response.json()["data"]["coinBalance"]) - float(response.json()["data"]["coinWithdrawBalance"])
        except Exception as e:
            print(e)

    def account_info(self):
        try:
            headers = {"Content-type": "application/json", "x-access-token": self.token}
            url = self.urlbase + "trade/account"
            response = requests.post(url, headers=headers)
            print(response.content)
            return response.json()
        except Exception as e:
            print(e)


    def cancel_order(self, symbol, order_id, amount, price, side):
        try:
            symbol = self.symbol_convert(symbol)
            headers = {"Content-type": "application/json", "x-access-token": self.token}
            url = self.urlbase + "trade/cancel"
            data = {"accno": self.accno, "accpwd": self.accpwd, "itemcode": symbol, "orderno": order_id, "sellbuyflag": side, "price": price, "amount": amount}
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            print(response.content)
        except Exception as e:
            print(e)

    def order_list(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            headers = {"Content-type": "application/json", "x-access-token": self.token}
            url = self.urlbase + "trade/list"
            data = {"accno": self.accno, "accpwd": self.accpwd, "itemcode": symbol, "request": "uncontract"}
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            # print(response.content)
            return response.json()["data"]
        except Exception as e:
            print(e)

        



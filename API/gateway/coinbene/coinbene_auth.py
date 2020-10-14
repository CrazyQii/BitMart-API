import requests
import json
import hashlib
import time
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Content-Type": "application/json;charset=utf-8", "Connection": "keep-alive"}

class CoinbeneAuth(object):
    def __init__(self, urlbase, api_id, secret):
        self.urlbase = urlbase
        self.api_id = api_id
        self.secret = secret

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def sign(self, data):
        try:
            signList = []
            data["secret"] = self.secret
            for key, value in data.items():
                signList.append(str(key) + "=" + str(value))
            signList.sort()
            signStr = "&".join(signList)
            signEncode = signStr.upper().encode()
            signHash = hashlib.md5()
            signHash.update(signEncode)
            return (signHash.hexdigest())
        except Exception as e:
            print(e)

    def place_order(self, symbol, quantity, price, type):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "trade/order/place"
            timestamp = long(time.time() * 1000)
            data = {"apiid": self.api_id, "symbol": symbol, "quantity": str(quantity), "price": str(price), "type": type, "timestamp": timestamp}
            signed = self.sign(data)
            data["sign"] = signed
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            print(response.content)
            return response.json()["orderid"]

        except Exception as e:
            print(e)

    def cancel_order(self, orderId):
        try:
            url = self.urlbase + "trade/order/cancel"
            timestamp = long(time.time() * 1000)
            data = {"apiid": self.api_id, "orderid": str(orderId), "timestamp": timestamp}
            signed = self.sign(data)
            data["sign"] = signed
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            return response.json()

        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            url = self.urlbase + "trade/balance"
            timestamp = long(time.time() * 1000)
            data = {"apiid": self.api_id, "account": "exchange", "timestamp": timestamp}
            signed = self.sign(data)
            data["sign"] = signed
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            balance = {}
            frozen = {}
            for i in response.json()["balance"]:
                balance[i["asset"]] = i["available"]
                frozen[i["asset"]] = i["reserved"]
            return balance, frozen

        except Exception as e:
            print(e)

    def order_detail(self, orderId):
        try:
            url = self.urlbase + "trade/order/info"
            timestamp = long(time.time() * 1000)
            data = {"apiid": self.api_id, "orderid": orderId, "timestamp": timestamp}
            signed = self.sign(data)
            data["sign"] = signed
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            return response.json()["order"]
        except Exception as e:
            print(e)

    def order_list(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "trade/order/open-orders"
            timestamp = long(time.time() * 1000)
            data = {"apiid": self.api_id, "symbol": symbol, "timestamp": timestamp}
            signed = self.sign(data)
            data["sign"] = signed
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            # print(response.content)
            return response.json()["orders"]["result"]
        except Exception as e:
            print(e)

if __name__ == "__main__":
    coinbene = CoinbeneAuth("https://api.coinbene.com/v1/",
                            "7cb17823db3b9740931052d0b7d09ef7",
                            "a69cb243106f45b1b2142b208beaa4e4")
    print (coinbene.order_list("APL_ETH"))
    # coinbene.place_order("APL_ETH", "1900900", "0.00000700", "sell-limit")
    a, b = coinbene.wallet_balance()
    print (a["ETH"], b["ETH"], a["APL"], b["APL"])

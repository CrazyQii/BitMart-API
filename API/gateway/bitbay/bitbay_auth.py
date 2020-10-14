from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import requests
import time
import re
import hashlib
import hmac
import urllib

class BitbayAuth(object):
    def __init__(self, urlbase, api_key, api_secret):
        self.url = urlbase + "Trading/tradingApi.php"
        self.api_key = api_key
        self.api_secret = api_secret

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base, symbol_quote
        except Exception as e:
            print(e)

    def sign(self, data):
        try:
            hash_data = hmac.new(self.api_secret, data, hashlib.sha512).hexdigest()
            return hash_data
        except Exception as e:
            print(e)

    def bitbay_request(self, data):
        try:
            timestamp = str(int(time.time()))
            data["moment"] = timestamp
            encode_data = urllib.urlencode(data)
            hash_data = hmac.new(self.api_secret, encode_data, hashlib.sha512).hexdigest()
            headers = {"API-Key": self.api_key, "API-Hash": hash_data, "Content-Type": "application/x-www-from-urlencoded"}
            response = requests.post(self.url, headers=headers, data=encode_data)
            return response
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            data = {"method": "info"}
            response = self.bitbay_request(data)
            print response.content
        except Exception as e:
            print(e)

    def get_history(self, currency, limit):
        try:
            data = {"method": "history", "currency": currency, "limit": limit}
            response = self.bitbay_request(data)
            print response.content
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        try:
            symbol_base, symbol_quote = self.symbol_convert(symbol)
            data = {"method": "trade", "currency": symbol_base, "payment_currency": symbol_quote, "amount": amount, "rate": price, "type": side}
            response = self.bitbay_request(data)
            order_id = json.loads(response.content)["order_id"]
            print order_id
            return order_id
        except Exception as e:
            print(e)

    def cancel_order(self, order_id):
        try:
            data = {"method": "cancel", "id": order_id}
            response = self.bitbay_request(data)
            print response.content
        except Exception as e:
            print(e)

    def order_list(self, symbol):
        try:
            symbol_base, symbol_quote = self.symbol_convert(symbol)
            data = {"method": "orders", "oeder_currency": symbol_base, "payment_currency": symbol_quote}
            response = json.loads(self.bitbay_request(data).content)
            order_list = []
            for order in response:
                order_list.append({"status": 1,
                                   "remaining_amount": order["units"],
                                   "timestamp": order["order_date"],
                                   "price": order["start_price"],
                                   "executed_amount": float(order["start_units"]) - float(order["units"]),
                                   "side": "buy" if order["type"] == "bid" else "sell",
                                   "fees": None,
                                   "original_amount": order["start_units"],
                                   "symbol": symbol,
                                   "entrust_id": order["order_id"]})
            return order_list
        except Exception as e:
            print(e)


if __name__ == "__main__":
    bitbay = BitbayAuth("https://bitbay.net/API/",
                        "ec5a3458-eee9-4b96-8249-1f6006be2dbb",
                        "26642543-783e-4c01-9b14-45628de892ce")
    print bitbay.order_list("BOB_BTC")
    # bitbay.wallet_balance()
    # print bitbay.place_order("BOB_BTC", "1000", "1", "sell")
    # bitbay.cancel_order("13742532105846")
    # bitbay.order_list("BOB_BTC")
    # bitbay.get_history("USDT", 10)
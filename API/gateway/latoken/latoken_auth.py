from os import sys, path
import os
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import json
import requests
import time, datetime
import re
import hmac
import hashlib

class LatokenAuth(object):
    def __init__(self, urlbase, api_key, api_secret):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def sign_message(self, endpoint, params):
        try:
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
            return hmac.new(self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest(), query
        except Exception as e:
            print (e)

    def place_order(self, symbol, amount, price, side):
        try:
            baseUrl = 'https://api.latoken.com'
            endpoint = '/api/v1/order/new'
            params = {'symbol': ''.join(symbol.split('_')),
                    'side': side.lower(),
                    'price': price,
                    'amount': amount,
                    'orderType': 'limit',
                    'timestamp': int(datetime.datetime.now().timestamp()*1000)}
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
                  
            signature = hmac.new(
                self.api_secret, 
                (endpoint + query).encode('ascii'), 
                hashlib.sha256
            )
            url = baseUrl + endpoint + query
            response = requests.post(
                url,
                headers = {
                    'X-LA-KEY': self.api_key,
                    'X-LA-SIGNATURE': signature.hexdigest(),
                    'X-LA-HASHTYPE': "HMAC-SHA256"
                }
            )
            return response.json()["orderId"]
        except Exception as e:
            print("place_order" + str(e))

    def order_detail(self, order_id):
        try:
            baseUrl = 'https://api.latoken.com'
            endpoint = '/api/v1/order/get_order'
            params = {'orderId': order_id}
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
                  
            signature = hmac.new(
                self.api_secret, 
                (endpoint + query).encode('ascii'), 
                hashlib.sha256
            )
            url = baseUrl + endpoint + query
            response = requests.get(
                url,
                headers = {
                    'X-LA-KEY': self.api_key,
                    'X-LA-SIGNATURE': signature.hexdigest(),
                    'X-LA-HASHTYPE': "HMAC-SHA256"
                }
            )
            raw_data = response.json()

            return {"status": 1, "remaining_amount": raw_data["remainingAmount"], "timestamp": raw_data["timeCreated"], 
                    "price": raw_data["price"], "executed_amount": raw_data["executedAmount"], "symbol": raw_data["symbol"], 
                    "fees": None, "original_amount": raw_data["amount"], "entrust_id": raw_data["orderId"], "side": raw_data["side"]}
        except Exception as e:
            print("order_detail" + str(e))

    def cancel_order(self, order_id):
        try:
            baseUrl = 'https://api.latoken.com'
            endpoint = '/api/v1/order/cancel'
            params = {"orderId": order_id,
                        "timestamp": int(datetime.datetime.now().timestamp()*1000)}
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
                  
            signature = hmac.new(
                self.api_secret, 
                (endpoint + query).encode('ascii'), 
                hashlib.sha256
            )
            url = baseUrl + endpoint + query
            response = requests.post(
                url,
                headers = {
                    'X-LA-KEY': self.api_key,
                    'X-LA-SIGNATURE': signature.hexdigest(),
                    'X-LA-HASHTYPE': "HMAC-SHA256"
                }
            )
            return response.json()
        except Exception as e:
            print("cancel_order" + str(e))

    def cancel_all(self, symbol):
        try:
            baseUrl = 'https://api.latoken.com'
            endpoint = '/api/v1/order/cancel_all'
            params = {"symbol": ''.join(symbol.split('_')),
                        "timestamp": int(datetime.datetime.now().timestamp()*1000)}
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
                  
            signature = hmac.new(
                self.api_secret, 
                (endpoint + query).encode('ascii'), 
                hashlib.sha256
            )
            url = baseUrl + endpoint + query
            response = requests.post(
                url,
                headers = {
                    'X-LA-KEY': self.api_key,
                    'X-LA-SIGNATURE': signature.hexdigest(),
                    'X-LA-HASHTYPE': "HMAC-SHA256"
                }
            )
            return response.json()
        except Exception as e:
            print("cancel_all" + str(e))

    def wallet_balance(self):
        try:
            baseUrl = 'https://api.latoken.com'
            endpoint = '/api/v1/account/balances'
            params = {'timestamp': int(datetime.datetime.now().timestamp()*1000)}
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
                  
            signature = hmac.new(
                self.api_secret, 
                (endpoint + query).encode('ascii'), 
                hashlib.sha256
            )
            url = baseUrl + endpoint + query
            response = requests.get(
                url,
                headers = {
                    'X-LA-KEY': self.api_key,
                    'X-LA-SIGNATURE': signature.hexdigest(),
                    'X-LA-HASHTYPE': "HMAC-SHA256"
                }
            )
            return response.json()
        except Exception as e:
            print("wallet_balance" + str(e))

    def order_list(self, symbol):
        try:
            baseUrl = 'https://api.latoken.com'
            endpoint = '/api/v1/order/active'
            params = {'symbol': ''.join(symbol.split('_')), 
                       'timestamp': int(datetime.datetime.now().timestamp()*1000)}
            queryParams = map(lambda it : it[0] + '=' + str(it[1]), params.items())
            query = '?' + '&'.join(queryParams)
                  
            signature = hmac.new(
                self.api_secret, 
                (endpoint + query).encode('ascii'), 
                hashlib.sha256
            )
            url = baseUrl + endpoint + query
            response = requests.get(
                url,
                headers = {
                    'X-LA-KEY': self.api_key,
                    'X-LA-SIGNATURE': signature.hexdigest(),
                    'X-LA-HASHTYPE': "HMAC-SHA256"
                }
            )
            raw_data = response.json()
            ods = []
            for o in raw_data:
                ods.append({"status": 1, "remaining_amount": o["remainingAmount"], "timestamp": o["timeCreated"], 
                    "price": o["price"], "executed_amount": o["executedAmount"], "symbol": o["symbol"], 
                    "fees": None, "original_amount": o["amount"], "entrust_id": o["orderId"], "side": o["side"]})
            return ods
        except Exception as e:
            print("open_orders" + str(e))

if __name__ == "__main__":
    latoken_auth = LatokenAuth(
        "https://api.latoken.com/v1/api",
        "0f15c941-ee38-4241-b411-6f5a8e16ea7a",
        b"NmJlZTAwZTgtMTY3YS00ZTliLWJiNzItMDMwZTQwMTQ1NjQx")
    # print(latoken_auth.place_order("APL_BTC", 100, 0.0000000600, "buy"))
    # print(latoken_auth.order_detail("30d04113-2b06-4550-9c93-c9a0c147998a"))
    # print(latoken_auth.cancel_order("f5184568-e52f-4d5a-9881-4d467ad68cdc"))
    # print(latoken_auth.cancel_all("APL_BTC"))
    print(latoken_auth.wallet_balance())
    # print(latoken_auth.open_orders("APL_BTC"))
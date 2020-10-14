from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from gateway.bitmart.bitmart_auth import BitMartAuth
from gateway.bitmart.bitmart_public import BitMartPublic
from gateway.bitmart.ref_bitmart_public import RefBitMartPublic
from gateway.bitmart.access_token import AccessToken
import re
import json
import random
import requests
from key.temp_production_key import *

def get_token_secret(base_url, account_key):
    try:
        api_key = account_key["api_key"]
        api_secret = account_key["api_secret"]
        memo = account_key["memo"]
        access_token = AccessToken(base_url, api_key, api_secret, memo)
        token = access_token.get_access_token()
        return (token, api_secret)
    except Exception as e:
        print(e)

class SelfTrading(object):
    def __init__(self, base_url, token, secret):
        self.exchange_auth = BitMartAuth(base_url, token, secret)
        self.exchange_public = BitMartPublic(base_url)
    
    def get_ask_bid_price(self, orderbook):
        ask_price, bid_price = 0, 0
        if "buys" in orderbook.keys():
            order_buys = orderbook["buys"]
            order_sells= orderbook["sells"]
            bid_price = float(order_buys[0]["price"])
            ask_price = float(order_sells[0]["price"])

        return ask_price, bid_price

    def get_price(self, symbol, ask_price, bid_price, symbol_price, spread):
        try:
            price_increment = self.exchange_public.get_price_increment(symbol)
            price_precision = self.exchange_public.get_price_precision(symbol)
            if ask_price - bid_price <= price_increment:
                return 0
            mul = random.choice([4, 5, 6])
            avg_price = (mul*ask_price + (10 - mul)*bid_price)/10
            if bid_price <= symbol_price <= ask_price:
                if avg_price <= symbol_price - 2*spread:
                    price = random.uniform(symbol_price- 2*spread, symbol_price)
                elif avg_price >= symbol_price + 2*spread:
                    price = random.uniform(symbol_price, symbol_price + 2*spread)
                else:
                    price = avg_price
            else:
                price = avg_price

            price = round(price, price_precision)
            return price
        except Exception as e:
            print("get price error: %s" % e)
            return 0
    def get_amount(self, symbol, lower, upper):
        try:
            amount_precision = self.exchange_public.get_amount_precision(symbol)
            amount = random.uniform(lower, upper)
            if amount_precision == 0:
                amount = int(amount)
            else:
                amount = round(amount, amount_precision)
            return amount
        except Exception as e:
            print("get amount error: %s" % e)
            return 0

    def build_volume(self, symbol, amount, price, symbol_price):
        try:
            bid_id = ""
            ask_id = ""
            if price < symbol_price:
                bid_id = self.exchange_auth.place_order(symbol, amount, price, "buy")
                ask_id = self.exchange_auth.place_order(symbol, amount, price, "sell")
            else:
                ask_id = self.exchange_auth.place_order(symbol, amount, price, "sell")
                bid_id = self.exchange_auth.place_order(symbol, amount, price, "buy")
                
            print("Volume - Symbol: %s, Amount: %s, Price: %s, BidId: %s, AskId: %s" % (
                symbol, amount, price, bid_id, ask_id))

            self.exchange_auth.cancel_order(bid_id)

            self.exchange_auth.cancel_order(ask_id)

        except Exception as e:
            print(e)

    def build_oc_volume(self, symbol, amount, price, symbol_price):
        try:
            if price < symbol_price:
                code = self.exchange_auth.place_oc_order(symbol, amount, price, "buy")
            else:
                code = self.exchange_auth.place_oc_order(symbol, amount, price, "sell")

            print("Volume -Code- Symbol: %s, Amount: %s, Price: %s, Code: %s" % (
                symbol, amount, price, code))
        except Exception as e:
            print(e)
            
    def creat_order(self, symbol, lower, upper, spread):
        try:
            symbol_price = self.exchange_public.get_price(symbol)
            if symbol_price == 0:
                print("Abnormal symbol price, suspend the program")

            orderbooks = self.exchange_public.get_orderbook(symbol)
            ask_price, bid_price = self.get_ask_bid_price(orderbooks)

            price = self.get_price(symbol, ask_price, bid_price, symbol_price, spread)
            amount= self.get_amount(symbol, lower, upper)

            if price == 0:
                print("Abnormal price, suspend the program")
                return

            if amount == 0:
                print("Abnormal amount, suspend the program")
                return

            self.build_oc_volume(symbol, amount, price, symbol_price)
            # if symbol in ["ETH_USDT"]:
            #     self.build_oc_volume(symbol, amount, price, symbol_price)
            # else:
            #     self.build_volume(symbol, amount, price, symbol_price)

        except Exception as e:
            print(e)
    
# if __name__ == "__main__":
#     base_url = "https://openapi.bitmart.com/v2/"
#     eos_usdt ={"api_key": "",
#                 "api_secret": "",
#                 "memo": "mm"
#                 }
#     token, secret = get_token_secret(base_url, eth_usdt)
#     self_trade = SelfTrading(base_url, token, secret)
#     while True:
#         self_trade.creat_order("ETH_USDT", 1, 10, 0.05)

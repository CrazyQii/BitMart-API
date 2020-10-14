from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from key import bw_token
import re
import os
import requests
import hashlib
import json
import time
import random
from bw.bw_public import BwPublic
try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode
from exchange_auth import ExchangeAuth

class BwAuth(ExchangeAuth):
    def __init__(self, urlbase, api_key, api_secret):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.market_list = {}        # id: market name
        self.currency_list = {}      # currency name: id

    def sign_message(self, data, timestamp):
        try:
            message = self.api_key + str(timestamp) + str(data) + self.api_secret
            signature = hashlib.md5(message.encode()).hexdigest()
            # print(message)
            return signature
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        try:
            market_id = self.get_market_id(symbol)
            data = json.dumps({"amount": amount,
                                "type": 0 if side == "sell" else 1,
                                "rangeType": 0,
                                "marketId": market_id,
                                "price": price})
            timestamp = str(int((time.time() * 1000)))
            sign = self.sign_message(data, timestamp)
            url = self.urlbase + "exchange/entrust/controller/website/EntrustController/addEntrust"
            headers = {"Apiid": self.api_key,
                        "Timestamp": timestamp,
                        "Sign": sign,
                        "Content-Type": "application/json"}
            is_ok, content = self.request("POST", url, data, headers)
            if is_ok:
                return content["datas"]["entrustId"]
            else:
                self.output("place_order", content)

        except Exception as e:
            print(e)

    def cancel_order(self, symbol, entrust_id):
        try:
            market_id = self.get_market_id(symbol)
            data = json.dumps({"entrustId": entrust_id,
                                "marketId": market_id})
            timestamp = str(int((time.time() * 1000)))
            sign = self.sign_message(data, timestamp)
            url = self.urlbase + "exchange/entrust/controller/website/EntrustController/cancelEntrust"
            headers = {"Apiid": self.api_key,
                        "Timestamp": timestamp,
                        "Sign": sign,
                        "Content-Type": "application/json"}
            is_ok, content = self.request("POST", url, data, headers)

            info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": content
            }
            print(info)
            return is_ok

        except Exception as e:
            print(e)

    def order_detail(self, symbol, entrust_id):
        try:
            market_id = self.get_market_id(symbol)
            data = {"entrustId": entrust_id,
                    "marketId": market_id}
            message = ""
            for key in sorted(data.keys()):
                message += (key + str(data[key]))
            timestamp = str(int((time.time() * 1000)))
            sign = self.sign_message(message, timestamp)
            url = self.urlbase + "exchange/entrust/controller/website/EntrustController/getEntrustById"
            headers = {"Apiid": self.api_key,
                        "Timestamp": timestamp,
                        "Sign": sign}
            is_ok, content = self.request("POST", url, data=data, headers=headers)
            if is_ok:
                return {"status": None,
                        "remaining_amount": float(content["datas"]["amount"]) - float(content["datas"]["completeAmount"]),
                        "timestamp": content["datas"]["createTime"],
                        "price": content["datas"]["price"],
                        "executed_amount": content["datas"]["completeAmount"],
                        "symbol": symbol,
                        "fees": None,
                        "original_amount": content["datas"]["amount"],
                        "entrust_id": content["datas"]["entrustId"],
                        "side": "sell" if content["datas"]["type"] == 0 else ("buy" if content["datas"]["type"] == 1 else "canceled")}
            else:
                self.output("order_detail", content)

        except Exception as e:
            print(e)
    
    def open_orders(self, symbol):
        page_index = 1
        orders = []
        try:
            ods = self.open_orders_page(symbol, page_index)
            while len(ods) > 0:
                orders.extend(ods)
                page_index += 1
                ods = self.open_orders_page(symbol, page_index)
            return orders
        except Exception as e:
            print(e)

    def open_orders_page(self, symbol, page):
        try:
            market_id = self.get_market_id(symbol)
            data = {"marketId": market_id,
                    "pageIndex": page,
                    "pageSize": 100}
            message = ""
            for key in sorted(data.keys()):
                message += (key + str(data[key]))
            timestamp = str(int((time.time() * 1000)))
            sign = self.sign_message(message, timestamp)
            url = self.urlbase + "exchange/entrust/controller/website/EntrustController/getUserEntrustRecordFromCacheWithPage"
            headers = {"Apiid": self.api_key,
                        "Timestamp": timestamp,
                        "Sign": sign}
            is_ok, content = self.request("POST", url, data=data, headers=headers)

            if is_ok:
                orders = []
                for order in content["datas"]["entrustList"]:
                    orders.append({"status": None,
                                    "remaining_amount": order["availabelAmount"],
                                    "timestamp": order["createTime"],
                                    "price": order["price"],
                                    "executed_amount": order["completeAmount"],
                                    "symbol": symbol,
                                    "fees": None,
                                    "original_amount": order["amount"],
                                    "entrust_id": order["entrustId"],
                                    "side": "sell" if order["type"] == 0 else ("buy" if order["type"] == 1 else "canceled")})

                return orders
            else:
                self.output("open_orders", content)

        except Exception as e:
            print(e)

    def get_currency_name(self, currency_id):
        try:
            if currency_id in self.currency_list.keys():
                return self.currency_list[currency_id]
            else:
                current_path = os.path.dirname(os.path.abspath(__file__))
                with open(current_path + "/bw_currencies_details.json", "r") as f:
                    currency_details = json.load(f)
                f.close()

                for currency in currency_details:
                    if str(currency["currencyId"]) == str(currency_id):
                        self.currency_list[currency_id] = currency["name"].upper()
                        return currency["name"].upper()

        except Exception as e:
            print(e)

    def get_market_id(self, market_name):
        try:
            if market_name in self.market_list.keys():
                return self.market_list[market_name]
            else:
                current_path = os.path.dirname(os.path.abspath(__file__))
                with open(current_path + "/bw_markets_details.json", "r") as f:
                    market_details = json.load(f)
                f.close()

                for market in market_details:
                    if str(market["name"]).upper() == str(market_name).upper():
                        self.market_list[market_name] = market["marketId"]
                        return market["marketId"]

        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            data = json.dumps({"pageSize":30, "pageNum":1})
            timestamp = str(int((time.time() * 1000)))
            sign = self.sign_message(data, timestamp)
            url = self.urlbase + "exchange/fund/controller/website/fundcontroller/findbypage"
            headers = {"Apiid": self.api_key,
                        "Timestamp": timestamp,
                        "Sign": sign,
                        "Content-Type": "application/json"}
            is_ok, content = self.request("POST", url, data, headers)
            if is_ok:
                free, frozen = {}, {}
                for currency in content["datas"]["list"]:
                    currency_id = currency["currencyTypeId"]
                    currency_name = self.get_currency_name(currency_id)
                    free[currency_name], frozen[currency_name] = currency["amount"], currency["freeze"]
                return free, frozen
            else:
                self.output("wallet_balance", content)
                return {}, {}

        except Exception as e:
            print(e)


if __name__ == "__main__":
    # bw1 = {"api_key": "7nawIZptdia7nawIZptdib",
            # "api_secret": "7a59d2840043d9644be44ce4b72fc870"}

    api_id = bw_token.sdc["api_key"]
    secret = bw_token.sdc["api_secret"]

    # bw_auth = BwAuth("https://www.BW.com/", bw["api_key"], bw["api_secret"])
    bw_auth = BwAuth("https://www.BW.com/", api_id, secret)
    bw_public = BwPublic("https://www.BW.com/")
    # print(bw_auth.sign_message(1,1))
    # print(bw_auth.place_order("SDC_ETH", 345.572, 0.000212, "buy"))
    # print(bw_auth.place_order("SDC_ETH", 1500, 0.000234, "sell"))
    # print(bw_auth.place_order("SDC_ETH", 1300, 0.000222, "buy"))
    # print(bw_auth.place_order("SDC_ETH", 3350, 0.000385, "sell"))


    # for i in range(1000):
    while True:
        try:
            num = random.randint(3000,8000) / 10.0
            price = random.randint(215, 220) / 1000000.0
            print (num, price)
            ask1_price = float(bw_public.get_orderbook("SDC_ETH")["sells"][0]["price"])
            if price < ask1_price and i % 5 == 0:
                print("Ask 1 Price: %s" % ask1_price)
                randnum = random.random()
                if randnum > 0.5:
                    print(bw_auth.place_order("SDC_ETH", num, price, "buy"))
                    print(bw_auth.place_order("SDC_ETH", num, price, "sell"))
                else:
                    print(bw_auth.place_order("SDC_ETH", num, price, "sell"))
                    print(bw_auth.place_order("SDC_ETH", num, price, "buy"))

            ods = bw_auth.open_orders("SDC_ETH")
            sorted_ods = sorted(ods, key = lambda i: float(i["timestamp"]))
            buy_ods = [o for o in sorted_ods if o["side"] == "buy"]
            print("Number of buy orders: %s" % len(buy_ods)) 
            if len(buy_ods) > 25:
                for i in range(len(buy_ods) - 25):
                    bw_auth.cancel_order("SDC_ETH", buy_ods[i]["entrust_id"])
            print(bw_auth.wallet_balance())
            time.sleep(random.randint(5, 30))
        except:
            time.sleep(10)
            continue


    # print(bw_auth.wallet_balance())
    # oid = bw_auth.place_order("BTC_USDT", 1, 9200, "buy")
    # print(bw_auth.cancel_order("SDC_ETH", "E6549746640146751488"))
    # print(bw_auth.cancel_order("SDC_ETH", "E6549746641535066112"))
    # print(bw_auth.order_detail("BTC_USDT", oid))
    # print(bw_auth.open_orders("SDC_ETH"))
    # ods = bw_auth.open_orders("SDC_ETH")
    # print (len(ods))
    # count = 0
    # for od in ods:
        # if od["side"] == "buy" and float(od["price"]) <= 0.000200:
            # bw_auth.cancel_order("SDC_ETH", od["entrust_id"])
            # print(od["price"], od["remaining_amount"], count)
            # count += 1
    # print(bw_auth.wallet_balance())
    # print(bw_auth.get_currency_name(6))
    # print(bw_auth.get_market_id("ETH_USDT"))

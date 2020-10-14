from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import re
import json
import random
import requests

def http_get_data(exchange, symbol):
    try:
        data = {}
        url = "http://mmaker-quote-v1-master/api/quote/get/%s/%s" % (exchange, symbol)
        ret = requests.get(url)
        if ret.status_code == 200:
            data = json.loads(ret.text)
            if data["header"]["code"] == 200:
                data = data["data"]
            else:
                data = {}
        return data
    except Exception as e:
        print(e)
        return {}

def get_price(exchange, symbol):
    price = 0
    data = http_get_data(exchange, symbol)
    if data:
        price = data["trade_price"]
    return price

def get_orderbook(exchange, symbol):
    orderbook = {}
    data = http_get_data(exchange, symbol)
    if data:
        orderbook["ask"] = [data["ask_price_1"], data["ask_volume_1"]]
        orderbook["bid"] = [data["bid_price_1"], data["bid_volume_1"]]
    return orderbook


if __name__ == "__main__":
    print("BNB", get_price("BNB", "BTC_USDT"))
    print("BNB", get_orderbook("BNB", "EOS_USDT"))
    print("BNB",get_orderbook("BNB", "LTC_USDT"))
    print("HB", get_price("HB", "BTC_USDT"))
    print("HB", get_orderbook("HB", "EOS_USDT"))
    print("HB",get_orderbook("HB", "BSV_USDT"))
    print("OK", get_price("OK", "BTC_USDT"))
    print("OK", get_orderbook("OK", "EOS_USDT"))
    print("OK",get_orderbook("OK", "LTC_USDT"))
    print("BM", get_price("BM", "BTC_USDT"))
    print("BM", get_orderbook("BM", "EOS_USDT"))
    print("BM",get_orderbook("BM", "LTC_USDT"))

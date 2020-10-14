
from abc import ABCMeta, abstractmethod
import traceback
import re
import json
import random
import requests

class ExchangePublic(object):
    def __init__(self, base_url):
        self.base_url = base_url

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

    def output(self, function_name, content):
        info = {
            "func_name": function_name,
            "response": content
        }
        print(info)

    @abstractmethod
    def get_price(self, symbol):
        pass

    @abstractmethod
    def get_orderbook(self, symbol):
        pass

    @abstractmethod
    def get_kline(self, symbol, timeperiod=360, interval=1):
        pass

    @abstractmethod
    def get_price_precision(self, symbol):
        pass

    @abstractmethod
    def get_price_increment(self, symbol):
        pass

    @abstractmethod
    def get_trades(self, symbol):
        pass 

    @abstractmethod
    def get_last_trade(self, symbol):
        pass

    def is_valid_price(self, symbol):
        return True

    def get_exchange_status(self):
        return True


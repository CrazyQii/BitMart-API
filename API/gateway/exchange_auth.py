from abc import ABCMeta, abstractmethod
import requests
import re
import json
import random
import traceback

class ExchangeAuth(object):
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
        print (info)

    @abstractmethod
    def place_order(self, symbol, amount, price, side):
        pass

    @abstractmethod
    def cancel_order(self, order_id, symbol=""):
        pass

    @abstractmethod
    def order_details(self, order_id, symbol=""):
        pass

    @abstractmethod
    def open_orders(self, symbol):
        pass

    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def get_trades(self, symbol):
        pass


        
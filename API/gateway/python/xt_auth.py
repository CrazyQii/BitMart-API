import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from restful import UbiexSDK

class XtAuth(object):
    def __init__(self, urlbase, key, secret):
        self.urlbase = urlbase
        self.xtsdk = UbiexSDK(key, secret)

    def symbol_convert(self, symbol):
        try:
            symbol = symbol.lower()
            return symbol
        except Exception as e:
            print(e)

    def output(self, function_name, content):
        info = {
            "func_name": function_name,
            "response": content.json()
        }
        print(info)

    def load_symbols_details(self):
        try:
            current_path = path.dirname(path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/vinex_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            symbol_details = self.load_symbols_details()
            return int(symbol_details[symbol]["amount_precision"])
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        try:
            symbol = self.symbol_convert(symbol)
            if side == "buy":
                type = 1
            elif side == "sell":
                type = 0
            res = self.xtsdk.order(symbol, price, amount, type, 0)
            if res["code"] == 200:
                print(res["info"])
                return res["data"]["id"]
            else:
                print(res["info"])
        except Exception as e:
            print(e)

    def cancel_order(self, symbol, entrust_id):
        try:
            symbol = self.symbol_convert(symbol)
            res = self.xtsdk.cancel(symbol, entrust_id)
            
            info = {
            "func_name": 'cancel_order',
            "entrust_id": entrust_id,
            "response": res["info"]
            }
            print(info)
        except Exception as e:
            print(e)

    def open_orders(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            res = self.xtsdk.getOpenOrders(symbol, 1, 1000)
            order_list = []
            if res["code"] == 200:
                for order in res["data"]:
                    if order["type"] == 0:
                        side = "buy"
                    elif order["type"] == 1:
                        side = "sell"
                    else:
                        side = "other"
                    order_list.append({
                        "symbol": symbol,
                        "entrust_id": order["id"],
                        "price": order["price"],
                        "side": side,
                        "original_amount": order["amount"],
                        "remaining_amount": float(order["amount"]) - float(order["completeNumber"]),
                        "timestamp": int(order["time"])
                    })
            return order_list
        except Exception as e:
            print(e)
    
    def order_detail(self, symbol, entrust_id):
        try:
            symbol = self.symbol_convert(symbol)
            res = self.xtsdk.getOrder(symbol, entrust_id)
            detail = {}
            if res["code"] == 200:
                order = res["data"]
                if order["type"] == 0:
                    side = "buy"
                elif order["type"] == 1:
                    side = "sell"
                else:
                    side = "other"
                detail = {
                "symbol": symbol,
                "entrust_id": order["id"],
                "price": order["price"],
                "side": side,
                "original_amount": order["amount"],
                "remaining_amount": float(order["amount"]) - float(order["completeNumber"]),
                "timestamp": int(order["time"])
                }
            return detail
        except Exception as e:
            print(e)

    def load_currency_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            currency_details = {}
            with open(current_path + "/xt_currency_details.json", "rb") as f:
                currency_details = json.load(f)
            f.close()
            return currency_details
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/xt_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            res = self.xtsdk.getBalance()
            free, frozen = {} ,{}
            if res["code"] == 200:
                data = res["data"]
                for coin in data.keys():
                    if float(data[coin]["freeze"]) + float(data[coin]["available"]) > 0:
                        free[coin.upper()] = float(data[coin]["available"])
                        frozen[coin.upper()] = float(data[coin]["freeze"])
            return free, frozen
        except Exception as e:
            print(e)

if __name__ == "__main__":
    xt_auth = XtAuth("", 
        "3ca33abe-e99e-4820-befa-4b24ae370e18", 
        "8b89ac95b6e261d2f53a0803d15cc5941588a322")
    # print(xt_auth.place_order("BTC_USDT", 1, 0.0005, "buy"))
    # print(xt_auth.wallet_balance())
    # order1 = xt_auth.place_order("HEX_USDT", 20, 0.00095, "buy")
    # order2 = xt_auth.place_order("HEX_USDT", 20, 0.00095, "sell")

    # o = xt_auth.open_orders("BTC_USDT")
    # print(o)
    # for i in o:
    #     xt_auth.cancel_order(i["entrust_id"])
    # print(xt_auth.order_detail("HEX_SXC", "E6653227871655538688"))
    # print(xt_auth.cancel_order("HEX_USDT", "E6653415791632953344"))
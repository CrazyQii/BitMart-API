import re
import requests
#import binance
import hashlib
import hmac
import time
try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode

ORDER_STATUS_NEW = 'NEW'
ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_EXPIRED = 'EXPIRED'

class BinanceAuth(object):
    def __init__(self, urlbase, api_key, api_secret,password=""):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.session()

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            if symbol_base == "GXC":
                symbol_base = "GXS"
            elif symbol_base == "BSV":
                symbol_base = "BCHSV"
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def sign(self, data):
        try:
            timestamp = str(int((time.time() * 1000)-1000))
            data["timestamp"] = timestamp
            encode_data = urlencode(data)
            byte_array = bytearray()
            byte_array.extend(self.api_secret.encode())
            signature = hmac.new(bytes(self.api_secret, encoding = "ascii"),
                                msg=bytes(encode_data, encoding = "ascii"),
                                digestmod=hashlib.sha256).hexdigest()
            data["signature"] = signature
            return data
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        try:
            symbol = self.symbol_convert(symbol)
            data = {"symbol": symbol, "quantity": amount, "price": format(price, ".8f"), "side": side, "type": "LIMIT", "timeInForce": "GTC"}
            data = self.sign(data)
            url = self.urlbase + "v3/order?" + str(urlencode(data))
            headers = {"X-MBX-APIKEY": self.api_key}
            response = self.session.post(url, headers=headers,verify=True)
            if response.status_code == 200:
                return response.json()["orderId"]
            else:
                print(response.json())
                return 
        except Exception as e:
            print(e)

    def cancel_order(self, symbol, order_id):
        try:
            symbol = self.symbol_convert(symbol)
            data = {"symbol": symbol, "orderId": order_id}
            data = self.sign(data)
            url = self.urlbase + "v3/order?" + str(urlencode(data))
            headers = {"X-MBX-APIKEY": self.api_key}
            response = self.session.delete(url, headers=headers, timeout=30, verify=True)
            return response.json()
        except Exception as e:
            print(e)

    def order_detail(self, symbol, order_id):
        try:
            uniform_symbol = symbol
            symbol = self.symbol_convert(symbol)
            data = {"symbol": symbol, "orderId": order_id}
            data = self.sign(data)
            url = self.urlbase + "v3/order?" + str(urlencode(data))
            headers = {"X-MBX-APIKEY": self.api_key}
            response = self.session.get(url, headers=headers, timeout=30, verify=True)

            if response.status_code == 200:
                return self.uniform_order(response.json(),uniform_symbol)
            else:
                detail_order={
                    "func_name": "detail_order",
                    "order_id": order_id,
                    "message": response.json(),  # "error info"
                    "data":{}
                }
                return detail_order
        except Exception as e:
            print(e)

    def open_orders(self, symbol):
        try:
            uniform_symbol = symbol
            symbol = self.symbol_convert(symbol)
            data = {"symbol": symbol}
            data = self.sign(data)
            url = self.urlbase + "v3/openOrders?" + str(urlencode(data))
            headers = {"X-MBX-APIKEY": self.api_key}
            response = self.session.get(url, headers=headers, timeout=30, verify=True).json()
            results = []
            if response:
                results = []
                for order in response:
                    results.append(self.uniform_order(order,uniform_symbol))
            return results
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            data = {}
            data = self.sign(data)
            url = self.urlbase + "v3/account?" + str(urlencode(data))
            headers = {"X-MBX-APIKEY": self.api_key}
            response = self.session.get(url, headers=headers, timeout=30, verify=True)
            if response.status_code == 200:
                response = response.json()
                balance = {i["asset"]: i["free"] for i in response["balances"]}
                frozen = {i["asset"]: i["locked"] for i in response["balances"]}
                return balance, frozen
            else:
                return response.json()

        except Exception as e:
            print(e)

    def uniform_order(self,order,symbol):

        oid = order["orderId"]
        filled_amount = float(order["executedQty"])
        price_avg = float(order["cummulativeQuoteQty"])/filled_amount if filled_amount > 0 else 0
        detail_order={
            "func_name": "detail_order",
            "order_id": oid,
            "message": "OK",  # "error info"
            "data":{
            "order_id": oid,
            "symbol":symbol,
            "side": order["side"],
            "price": float(order["price"]),
            "amount": float(order["origQty"]),
            "price_avg": price_avg,
            "filled_amount":filled_amount,
            "status": self.convert_status(order["status"]),
            "creare_time":order["time"]
            }
        }
        return detail_order


    def convert_status(self,status):
        '''
        1=下单失败
        2=创建订单中
        3=下单失败,冻结失败
        4=下单成功,等待成交
        5=部分成交
        6=完全成交
        7=撤销中
        8=撤销成功
        -----------------------------------------------
        NEW	订单被交易引擎接受
        PARTIALLY_FILLED	部分订单被成交
        FILLED	订单完全成交
        CANCELED	用户撤销了订单
        PENDING_CANCEL	撤销中(目前并未使用)
        REJECTED	订单没有被交易引擎接受，也没被处理
        EXPIRED	订单被交易引擎取消, 比如[
                                    LIMIT FOK 订单没有成交
                                    市价单没有完全成交
                                    强平期间被取消的订单
                                    交易所维护期间被取消的订单
                                    ]
        '''
        if status == "NEW":
            ret = 4
        elif status == "PARTIALLY_FILLED":
            ret = 5
        elif status == "FILLED":
            ret = 6
        elif status in ["CANCELED","EXPIRED"]:
            ret = 8
        elif status == "PENDING_CANCEL":
            ret = 7
        else:
            ret = 1
        return str(ret)


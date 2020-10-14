import requests
import json
import time
import os
import re
from coinzeus_token_access import AccessToken

class CoinzeusAuth(object):
    def __init__(self, urlbase, token, login_name):
        self.urlbase = urlbase
        self.login_name = login_name
        self.token = "Bearer " + token

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "/" + symbol_quote
        except Exception as e:
            print(e)

    def side_convert(self, side):
        try:
            if side == "sell":
                return ("ask")
            elif side == "buy":
                return ("bid")
            else:
                return side
        except Exception as e:
            print (e)

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

    '''
    @response
        request https://api2.coinzeus.io/account/balance
        response example:
        {
            "funcName":"balance",
            "status":"0",
            "message":"Success.",
            "data":
                {
                "total":
                {
                    "BTR":0.0,
                    "MARE":0.0,
                    "KDA":0.0,
                    "EYEAL":0.0,
                    "TMTG":0.0,
                    "WPC":0.0,
                    "ARTS":0.0,
                    "BTC":0.0,
                    ...
                }
            }
        }
    '''
    def get_balance(self):
        url = self.urlbase + "account/balance"
        headers = {"Authorization": self.token}
        data = {"mbId": self.login_name}
        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            return response["data"]
        else:
            print ("Error: get_balance() error. response:", response)

    '''
    @response
        request https://api2.coinzeus.io/trade/orderPlace
        response example 1:
        {
            u'status': u'5002',
            u'message': u'Insufficient balance.',
            u'funcName': u'orderPlace'
        }

        response example 2:
        {
            "funcName":"orderPlace",
            "status":"0",
            "message":"Success."
        }
    '''
    # @params
    # side: ask, bid
    def place_order(self, symbol, amount, price, side):
        side = self.side_convert(side)
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "trade/orderPlace"
        headers = {"Authorization": self.token}
        data = {
            "mbId": self.login_name,
            "pairName": symbol,
            "action": side,
            "price": price,
            "amount": amount
            }
        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            return response
        else:
            print("Error: place_order() error. response:", response)

    '''
    @params
        side: bid, ask
    @response
        request https://api2.coinzeus.io/trade/orderCancel
        response example:
        {
            "funcName":"orderCancel",
            "status":"0",
            "message":"Success."
        }
    '''
    def cancel_order(self, symbol, order_id, price, side):
        side = self.side_convert(side)
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "trade/orderCancel"
        headers = {"Authorization": self.token}
        data = {
            "mbId": self.login_name,
            "pairName": symbol,
            "ordNo": order_id,
            "action": side,
            "ordPrice": price}
        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            return response
        else:
            print("Error: calcel_order() error. response:", response)

    def cancel_all(self, symbol):
        try:
            open_orders = self.open_orders("WPC_BTC")
            print open_orders
            for i in open_orders:
                print self.cancel_order(symbol, i["entrust_id"], i["price"], i["side"])

        except Exception as e:
            print (e)


    ''' 
    @params
        action: bid, ask, all
    @response
        request https://api2.coinzeus.io/trade/openOrders
        response example:
    {u'status': u'0',
        u'message': u'Success.',
        u'data': {
            u'totalCnt': 1,
            u'list': [
                {
                    u'remainAmount': u'0.018',
                    u'ordPrice': u'0.033',
                    u'ordNo': 19020918826,
                    u'ordAmount': u'0.018',
                    u'pairName': u'ETH/BTC',
                    u'mbId': u'joydanevery@gmail.com',
                    u'action': u'ask',
                    u'ordDt': u'20190209151755'
                }
            ]
        },
        u'funcName': u'openOrders'
    }
    '''
    def open_orders(self, symbol):
        underline_symbol = symbol
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "account/openOrders"
        headers = {"Authorization": self.token}
        data = {
            "mbId": self.login_name,
            "pairName": symbol,
            "action": "all",
            "cnt": 200,
            "skipIdx": 0
            }
        is_ok, response = self.request("POST", url, headers=headers, data=data)
        if is_ok:
            open_orders = []
            for i in response["data"]["list"]:
                side = "buy"
                if i["action"] == "ask":
                    side = "sell"
                open_orders.append({
                    "symbol": underline_symbol,
                    "entrust_id": i["ordNo"],
                    "price": i["ordPrice"],
                    "side": side,
                    "original_amount": i["ordAmount"],
                    "remaining_amount": i["remainAmount"],
                    "timestamp": int(time.mktime(time.strptime(i["ordDt"], "%Y%m%d%H%M%S")))
                })
            return open_orders
        else:
            print ("Error: open_orders() error. response:", response)

if __name__ == "__main__":
    # token = AccessToken(
    #     "joydanevery@gmail.com", "c01nStart!",
    #     "Y3J5cHRvLWV4Y2hhbmdlLXdlYjo1YzFmZWIyZWUxOWQ4NTcyNzBkNjY1NzVkYjIzMTg0MzlhN2UwZmI0ODAyZTE0MTJhODYzMjc2ZjMwMTQ2ZThj").get_token()
    # print token
    token = AccessToken(
        "support@cryptopie.co.jp", "Chiisato62!",
        "Y3J5cHRvLWV4Y2hhbmdlLXdlYjo1YzFmZWIyZWUxOWQ4NTcyNzBkNjY1NzVkYjIzMTg0MzlhN2UwZmI0ODAyZTE0MTJhODYzMjc2ZjMwMTQ2ZThj").get_token()
    print token

    coinzeus_auth = CoinzeusAuth("https://api2.coinzeus.io/", token, "support@cryptopie.co.jp")
    # print coinzeus_auth.get_balance()
    # print coinzeus_auth.place_order("WPC_BTC", 1277, 0.00000505, "buy")
    # print coinzeus_auth.place_order("WPC_BTC", 127, 0.00000965, "sell")


    a = coinzeus_auth.open_orders("WPC_BTC")
    print a
    for i in a:
        print coinzeus_auth.cancel_order("WPC_BTC", (i["entrust_id"]), (i["price"]), i["side"])
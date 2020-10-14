# -*- coding: utf-8 -*-
"""
okex spot authentication API
2020/10/14 hlq
"""
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import datetime
import base64
import hmac
import json
from okex.okex_public import OkexPublic


class OkexAuth(OkexPublic):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
    
    def symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))
    
    def sign_message(self, data):
        try:
            mac = hmac.new(bytes(self.api_secret, encoding='utf8'), bytes(data, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            return base64.b64encode(d)
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        """
        Place order
        """
        try:
            url = self.urlbase + "api/spot/v3/orders"
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                    "type": "limit", 
                    "side": side, 
                    "instrument_id": self.symbol_convert(symbol), 
                    "size": amount,
                    "price": price
                    }
            message = ts + "POST" + "/api/spot/v3/orders" + json.dumps(params)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }

            is_ok, content = self._request("POST", url, data=json.dumps(params), headers=headers)
            if is_ok:
                return content["order_id"]
            else:
                self._output("place_order", content)
                return None
        except Exception as e:
            print(e)
            return None

    def cancel_order(self, symbol, entrust_id):
        """
        cancel order
        """
        try:
            url = self.urlbase + "api/spot/v3/cancel_orders/%s" % entrust_id
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                    "instrument_id": self.symbol_convert(symbol), 
                    "order_id": entrust_id
                    }
            message = ts + "POST" + "/api/spot/v3/cancel_orders/%s" % entrust_id + json.dumps(params)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            is_ok, content = self._request("POST", url, data=json.dumps(params), headers=headers)
            if is_ok:
                info = {
                    "func_name": 'cancel_order',
                    "entrust_id": entrust_id,
                    "response": content
                }
                print(info)
                return is_ok
            else:
                self._output("place_order", content)
                return None
        except Exception as e:
            print(e)
            return None

    def order_detail(self, symbol, entrust_id):
        """
        Get order detail
        """
        try:
            url = self.urlbase + "api/spot/v3/orders/%s" % entrust_id + "?instrument_id=%s" % self.symbol_convert(symbol)
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/orders/%s" % entrust_id + "?instrument_id=%s" % self.symbol_convert(symbol)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            is_ok, content = self._request("GET", url, headers=headers)
            order = {}
            if is_ok:
                order = {
                    "entrust_id": entrust_id,
                    "side": content["side"],
                    "symbol": symbol,
                    "status": content["state"],
                    "timestamp": content["created_at"],
                    "price": float(content["price"]),
                    "original_amount": float(content["size"]),
                    "executed_amount": float(content["filled_size"]),
                    "remaining_amount": float(content["size"]) - float(content["filled_size"]),
                    "fees": None
                }
            else:
                self._output("order_detail", content)
            return order
        except Exception as e:
            print(e)
            return None

    def open_orders(self, symbol):
        """
        Get a list of user orders
        """
        try:
            url = self.urlbase + "api/spot/v3/orders_pending" + "?instrument_id=%s" % self.symbol_convert(symbol)
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/orders_pending" + "?instrument_id=%s" % self.symbol_convert(symbol)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            is_ok, content = self._request("GET", url, headers=headers)
            results = []
            if is_ok:
                for order in content:
                    results.append({
                        "entrust_id": order["order_id"],
                        "side": order["side"],
                        "symbol": symbol,
                        "status": order["state"],
                        "timestamp": order["created_at"],
                        "price": float(order["price"]),
                        "original_amount": float(order["size"]),
                        "executed_amount": float(order["filled_size"]),
                        "remaining_amount": float(order["size"]) - float(order["filled_size"]),
                        "fees": None
                    })
            else:
                self._output("open_orders", content)
            return results
        except Exception as e:
            print(e)
            return None

    def wallet_balance(self):
        """
        Get the user's wallet balance for all currencies
        """
        try:
            url = self.urlbase + "api/spot/v3/accounts"
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/accounts"
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            is_ok, content = self._request("GET", url, headers=headers)
            free, frozen = {}, {}
            if is_ok:
                for currency in content:
                    free[currency["currency"]], frozen[currency["currency"]] = currency["available"], currency["hold"]
            else:
                self._output("wallet_balance", content)
            return free, frozen
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    okex = OkexAuth("https://www.okex.com/", "dda0063c-70fc-42b1-8390-281e77b532a5", "A06AFB73716F15DC1805D183BCE07BED", "okexpassphrase")
    # print(okex.place_order("XRP_BTC", 30, 0.0002, "sell"))
    # id1 = okex.place_order("XRP_BTC", 15, 0.0001, "sell")
    # id2 = okex.place_order("XRP_BTC", 10, 0.0002, "sell")
    # print(id1)
    # print(okex.order_detail("XRP_BTC", id1))
    # print(okex.open_orders("XRP_BTC"))
    # print(okex.cancel_order("XRP_BTC", id1))
    # print(okex.cancel_order("XRP_BTC", 'ddf'))
    # print(okex.wallet_balance())

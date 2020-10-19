# -*- coding: utf-8 -*-
"""
okex spot authentication API
2020/10/14 hlq
"""
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from datetime import datetime
import base64
import hmac
import json
import requests


class OkexAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
    
    def _symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))
    
    def sign_message(self, data):
        try:
            mac = hmac.new(bytes(self.api_secret, encoding='utf8'), bytes(data, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            return base64.b64encode(d)
        except Exception as e:
            print(e)

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + "api/spot/v3/orders"
            ts = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                    "type": "limit", 
                    "side": side, 
                    "instrument_id": self._symbol_convert(symbol),
                    "size": amount,
                    "price": price
                    }
            message = ts + "POST" + "/api/spot/v3/orders" + json.dumps(params)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }

            resp = requests.post(url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:
                resp = resp.json()
                if resp['result']:
                    return resp["order_id"]
                else:
                    print(resp['error_message'])
            else:
                print(f'Okex auth error: {resp.json()["message"]}')
            return None
        except Exception as e:
            print(f'Okex auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f"api/spot/v3/cancel_orders/{order_id}"
            ts = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                    "instrument_id": self._symbol_convert(symbol),
                    "order_id": order_id
                    }
            message = ts + "POST" + f"/api/spot/v3/cancel_orders/{order_id}" + json.dumps(params)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            resp = requests.post(url, data=json.dumps(params), headers=headers)
            data = False
            if resp.status_code == 200:
                resp = resp.json()
                data = resp['result']
                message = resp['error_message']
            else:
                resp = resp.json()
                message = resp['error_message']
                print(f'Okex auth error: {message}')

            info = {
                "func_name": "cancel_order",
                "order_id": order_id,
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Okex auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                info = {
                    "func_name": "cancel_order",
                    "message": None,
                    "data": False
                }
                return info

            order_ids = [order['order_id'] for order in orders if order['side'] == side]
            url = self.urlbase + "api/spot/v3/cancel_batch_orders"
            ts = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                "instrument_id": "-".join(symbol.split('_')).lower(),
                "order_ids": order_ids
            }
            message = ts + "POST" + f"/api/spot/v3/cancel_batch_orders[" + json.dumps(params) + "]"
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed,
                       "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase,
                       "Content-Type": "application/json"
                       }

            resp = requests.post(url, data=json.dumps(params), headers=headers)
            data = False
            if resp.status_code == 200:
                resp = resp.json()
                data = resp['result']
                message = resp['error_message']
            else:
                resp = resp.json()
                message = resp['error_message']
                print(f'Okex auth error: {message}')

            info = {
                "func_name": "cancel_order",
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Okex auth cancel order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f"api/spot/v3/orders/{order_id}?instrument_id={self._symbol_convert(symbol)}"
            ts = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + f"/api/spot/v3/orders/{order_id}?instrument_id={self._symbol_convert(symbol)}"
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            resp = requests.get(url, headers=headers)
            order_detail = {}
            if resp.status_code == 200:
                resp = resp.json()
                order_detail = {
                    "order_id": order_id,
                    "symbol": symbol,
                    "side": resp["side"],
                    "price": float(resp["price"]),
                    "amount": float(resp["size"]),
                    "price_avg": float(resp["price_avg"]),
                    "filled_amount": float(resp["filled_size"]),
                    "timestamp": self._utc_to_ts(resp["created_at"])
                }
            else:
                print(f'Okex auth error: {resp.json()["message"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp['message'],
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Okex auth order detail error: {e}')

    def open_orders(self, symbol: str, status=6, limit=100):
        try:
            url = self.urlbase + f"api/spot/v3/orders?instrument_id={self._symbol_convert(symbol)}&state={status}&limit={limit}"
            ts = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + f"/api/spot/v3/orders?instrument_id={self._symbol_convert(symbol)}&state={status}&limit={limit}"
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            resp = requests.get(url, headers=headers)
            results = []
            if resp.status_code == 200:
                resp = resp.json()
                for order in resp:
                    results.append({
                        "order_id": order['order_id'],
                        "symbol": symbol,
                        "side": order["side"],
                        "price": float(order["price"]),
                        "amount": float(order["size"]),
                        "price_avg": float(order["price_avg"]),
                        "filled_amount": float(order["filled_size"]),
                        "timestamp": self._utc_to_ts(order["timestamp"])
                    })
            else:
                print(f'Okex auth error: {resp.json()["message"]}')
            return results
        except Exception as e:
            print(f'Okex auth open order error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + "api/spot/v3/accounts"
            ts = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/accounts"
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            resp = requests.get(url, headers=headers)
            balance, frozen = {}, {}
            if resp.status_code == 200:
                wallet = resp.json()
                balance = {row["currency"]: float(row["available"]) for row in wallet}
                frozen = {row["currency"]: float(row["hold"]) for row in wallet}
            else:
                print(f'Okex auth error: {resp.json()["message"]}')
            return balance, frozen
        except Exception as e:
            print(f'Okex auth wallet balance error: {e}')
            return {}, {}


if __name__ == "__main__":
    okex = OkexAuth("https://www.okex.com/", "dda0063c-70fc-42b1-8390-281e77b532a5", "A06AFB73716F15DC1805D183BCE07BED", "okexpassphrase")
    # print(okex.place_order("XRP_BTC", 30, 0.0002, "sell"))
    # print(okex.cancel_order("XRP_BTC", '123'))
    # print(okex.order_detail("XRP_BTC", '123'))
    # print(okex.cancel_all('XRP_BTC', 'sell'))
    # print(okex.open_orders("XRP_BTC"))
    # print(okex.wallet_balance())

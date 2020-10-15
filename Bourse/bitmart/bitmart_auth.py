# -*- coding: utf-8 -*-
"""
bitmart spot authentication API
2020/10/10 hlq
"""

from Bourse.bitmart.bitmart_public import BitmartPublic
import hmac
import hashlib
import time
import json
import requests


class BitmartAuth(BitmartPublic):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, query_string):
        """ authtication """
        try:
            # signature string
            sign_str = f'{self._timestamp()}#{self.memo}#{query_string}'
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(sign_str, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def _timestamp(self):
        return str(round(time.time()*1000))

    def place_order(self, symbol: str, amount: float, price: float, side: str, type='limit'):
        if side not in ['buy', 'sell']:
            print('side is wrong')
            return None
        try:
            url = self.urlbase + '/spot/v1/submit_order'
            params = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'price': price,
                'size': amount
            }
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-SIGN': self._sign_message(json.dumps(params)),
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            if resp['code'] == 1000:
                return resp['data']['order_id']
            else:
                print(f'Bitmart auth error: {resp["message"]}')
                return None
        except Exception as e:
            print(f'Bitmart auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/spot/v2/cancel_order'
            params = {
                'symbol': symbol,
                'order_id': order_id,
            }
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-SIGN': self._sign_message(json.dumps(params)),
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }

            resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            data = False
            if resp['code'] == 1000:
                data = resp["data"]
                message = resp["message"]
            else:
                message = resp["message"]
                print(f'Bitmart auth error: {message}')

            info = {
                "func_name": "cancel_order",
                "order_id": order_id,
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Bitmart auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            url = self.urlbase + f'/spot/v1/cancel_orders'

            params = {
                'symbol': symbol,
                'side': side,
            }
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-SIGN': self._sign_message(json.dumps(params)),
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            resp = requests.post(url, data=json.dumps(params), headers=headers).json()

            data = False
            if resp['code'] == 1000:
                data = resp["data"]
                message = resp["message"]
            else:
                message = resp["message"]
                print(f'Bitmart auth error: {message}')

            info = {
                "func_name": "cancel_order",
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Bitmart auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        try:
            url = self.urlbase + f'/spot/v1/orders?symbol={symbol}&status={status}&offset={offset}&limit={limit}'
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            resp = requests.get(url, headers=headers).json()
            results = []
            if resp['code'] == 1000:
                for order in resp['data']['orders']:
                    results.append({
                        'order_id': order['order_id'],
                        'symbol': order['symbol'],
                        'original_amount': float(order['size']),
                        'price': float(order['price']),
                        'side': order['side'],
                        'price_avg': float(order['price_avg']),
                        'filled_amount': float(order['filled_size']),
                        'create_time': order['create_time']
                    })
            else:
                print(f'Bitmart auth error: {resp["message"]}')
            return results
        except Exception as e:
            print(f'Bitmart auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/spot/v1/order_detail?symbol={symbol}&order_id={order_id}'
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }

            resp = requests.get(url, headers=headers).json()
            order_detail = {}
            if resp['code'] == 1000:
                content = resp['data']
                order_detail = {
                    'order_id': content['order_id'],
                    'symbol': content['symbol'],
                    'side': content['side'],
                    'price': float(content['price']),
                    'amount': float(content['size']),
                    'price_avg': float(content['price_avg']),
                    'filled_amount': float(content['filled_size']),
                    'create_time': content['create_time']
                }
            else:
                print(f'Bitmart auth error: {resp["message"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp['message'],
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Bitmart auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/spot/v1/wallet'
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            resp = requests.get(url, headers=headers).json()
            balance, frozen = {}, {}
            if resp['code'] == 1000:
                wallet = resp["data"]["wallet"]
                balance = {row["id"]: float(row["available"]) for row in wallet}
                frozen = {row["id"]: float(row["frozen"]) for row in wallet}
            else:
                print(f'Bitmart auth error: {resp["message"]}')
            return balance, frozen
        except Exception as e:
            print(f'Bitmart auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = BitmartAuth('https://api-cloud.bitmart.info', '5de397b9cef8bebc31f65e124c3a4a162d6d1f99', 'f4b7c83dc9c6790d6ea344ba3beafdfd70fe9481dccc7e70f0dd7d84b76e1ed2', 'mock')
    # print(bit.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.wallet_balance())

# -*- coding: utf-8 -*-
"""
HuoBi spot authentication api
2020/10/13 hlq
"""

import datetime
import hmac
import hashlib
import base64
import requests
from urllib import parse


class HuoAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _get_timestamp(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def _set_params(self, signature, params: dict=None):
        try:
            res = {
                'AccessKeyId': self.api_key,
                "SignatureVersion": "2",
                "SignatureMethod": "HmacSHA256",
                "Timestamp": self._get_timestamp(),
            }
            if params is not None:
                for key, value in params.items():
                    res.update({key: value})
            res.update({'Signature': signature})
            return res
        except Exception as e:
            print(e)

    def _sign_message(self, method, host, path, params=None):
        try:
            if params is None:
                req_str = f'AccessKeyId={self.api_key}&' \
                          f'SignatureMethod=HmacSHA256&' \
                          f'SignatureVersion=2&' \
                          f'Timestamp={parse.quote(self._get_timestamp())}'
            else:
                par_str = '&'.join([f'{key}={value}' for key, value in params.items()])
                req_str = f'AccessKeyId={self.api_key}&' \
                          f'SignatureMethod=HmacSHA256&' \
                          f'SignatureVersion=2&' \
                          f'Timestamp={parse.quote(self._get_timestamp())}&' \
                          f'{par_str}'
            # concat string
            msg = f'{method}\n{host}\n{path}\n{req_str}'
            digest = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'),
                              digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(digest).decode()
            return sign
        except Exception as e:
            print(e)

    def _account_id(self):
        try:
            url = self.urlbase + '/v1/account/accounts'
            signature = self._sign_message('GET', 'api.huobi.pro', '/v1/account/accounts')
            params = self._set_params(signature)
            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            if resp['status'] == 'ok':
                for account in resp['data']:
                    if account['type'] == 'spot':
                        return account['id']
            else:
                print(resp['err-msg'])
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/v1/order/orders/place'

            account_id = self._account_id()
            params = {
                'account-id': account_id,
                'amount': amount,
                'price': price,
                'source': 'spot-api',
                'symbol': self._symbol_convert(symbol),
                'type': f'{side}-limit'
            }

            signature = self._sign_message('POST', 'api.huobi.pro', '/v1/order/orders/place', params)
            params = self._set_params(signature, params)

            resp = requests.post(url, data=params, headers={'Content-Type': 'application/json'}).json()
            if resp['status'] == 'ok':
                return resp['data']
            else:
                print(f'Huobi auth place order error: {resp["err-msg"]}')
                return None
        except Exception as e:
            print(f'Huobi auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/v1/order/orders/{order_id}/submitcancel'

            signature = self._sign_message('POST', 'api.huobi.pro', f'/v1/order/orders/{order_id}/submitcancel')
            params = self._set_params(signature)

            resp = requests.post(url, params=params).json()
            data = False
            if resp['status'] == 'ok':
                data = resp['data']
                message = resp['status']
            else:
                message = resp['err-msg']
            info = {
                "func_name": "cancel_order",
                "order_id": order_id,
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Huobi auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            url = self.urlbase + '/v1/order/orders/batchCancelOpenOrders'

            params = {
                'account-id': self._account_id(),
                'symbol': symbol,
                'side': side
            }
            signature = self._sign_message('POST', 'api.huobi.pro', '/v1/order/orders/batchCancelOpenOrders', params)
            params = self._set_params(signature, params)
            resp = requests.post(url, data=params, headers={'Content-Type': 'application/json'}).json()
            data = False
            if resp['status'] == 'ok':
                data = resp['data']
                message = resp['status']
            else:
                message = resp['err-msg']

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Huobi auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        try:
            url = self.urlbase + '/v1/order/openOrders'

            params = {
                'account-id': self._account_id(),
                'symbol': self._symbol_convert(symbol)
            }

            signature = self._sign_message('GET', 'api.huobi.pro', '/v1/order/openOrders', params)
            params = self._set_params(signature, params)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            results = []
            if resp['status'] == 'ok':
                for order in resp['data']:
                    results.append({
                        'order_id': order['id'],
                        'symbol': order['symbol'],
                        'side': order['type'],
                        'price': float(order['price']),
                        'amount': float(order['amount']),
                        'price_avg': None,
                        'filled_amount': float(order['field-amount']),
                        'create_time': round(order['created-at'] / 1000)
                    })
            else:
                print(f'Huobi auth open order error: {resp["err-msg"]}')
            return results
        except Exception as e:
            print(f'Huobi auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/v1/order/orders/{order_id}'

            signature = self._sign_message('GET', 'api.huobi.pro', f'/v1/order/orders/{order_id}')
            params = self._set_params(signature)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            order_detail = {}
            if resp['status'] == 'ok':
                order = resp['data']
                order_detail = {
                    'order_id': order_id,
                    'symbol': order['symbol'],
                    'side': order['type'],
                    'price': float(order['price']),
                    'amount': float(order['amount']),
                    'price_avg': None,
                    'filled_amount': float(order['field-amount']),
                    'create_time': round(order['created-at'] / 1000)
                }
            else:
                print(f'Huobi auth order detail error: {resp["err-msg"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp['err-msg'],
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Huobi auth order detail error: {e}')

    def wallet_balance(self):
        try:
            account_id = self._account_id()
            url = self.urlbase + f'/v1/account/accounts/{account_id}/balance'
            signature = self._sign_message('GET', 'api.huobi.pro', f'/v1/account/accounts/{account_id}/balance')
            params = self._set_params(signature)
            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            balance, frozen = {}, {}
            if resp['status'] == 'ok':
                for currency in resp['data']['list']:
                    if currency['type'] == 'trade':
                        balance[currency['currency']] = currency['balance']
                    if currency['type'] == 'frozen':
                        frozen[currency['currency']] = currency['balance']
            else:
                print(f'Huobi auth wallet balance error: {resp["message"]}')
            return balance, frozen
        except Exception as e:
            print(f'Huobi auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    huo = HuoAuth('https://api.huobi.pro', '7f5dffb3-ur2fg6h2gf-31a3e34b-f14f0', '86fdfa61-06ed4556-042c0f72-4665f')
    # print(huo.place_order('EOS_USDT', 1.0016, 11, 'sell'))
    # print(huo.cancel_order('EOS_USDT', '234'))
    # print(huo.cancel_all('EOS_USDT', 'sell'))
    # print(huo.open_orders('EOS_USDT'))
    # print(huo.order_detail('EOS_USDT', '234'))
    # print(huo.wallet_balance())

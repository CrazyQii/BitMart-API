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
import operator
from urllib.parse import urlencode


class HuoAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _ts_to_uts(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def _sign_message(self, method, host, path, params):
        try:
            # post请求，自带参数不参与验证
            if method == 'POST':
                params = {
                    'AccessKeyId': params['AccessKeyId'],
                    'SignatureMethod': params['SignatureMethod'],
                    'SignatureVersion': params['SignatureVersion'],
                    'Timestamp': params['Timestamp']
                }
                string = urlencode(params)
                msg = f'{method}\n{host}\n{path}\n{string}'
            else:
                # get请求，参数排序并验证
                sort = sorted(params.items(), key=operator.itemgetter(0))
                string = urlencode(sort)
                msg = f'{method}\n{host}\n{path}\n{string}'
            digest = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'),
                              digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(digest).decode()
            return sign
        except Exception as e:
            print(e)

    def _set_params(self, method, host, path, params: dict = None):
        try:
            ts = self._ts_to_uts()
            res = {  # 请求公共参数
                'AccessKeyId': self.api_key,
                'SignatureMethod': 'HmacSHA256',
                'SignatureVersion': '2',
                'Timestamp': ts
            }
            if params is None:
                Signature = self._sign_message(method, host, path, res)
                res.update({'Signature': Signature})
            else:
                for key, value in params.items():
                    res.update({key: value})
                Signature = self._sign_message(method, host, path, res)
                res.update({'Signature': Signature})
            return res
        except Exception as e:
            print(e)

    def _account_id(self):
        try:
            url = self.urlbase + '/v1/account/accounts'
            params = self._set_params('GET', 'api.huobi.pro', '/v1/account/accounts')
            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            if resp['status'] == 'ok':
                for account in resp['data']:
                    if account['type'] == 'spot' and account['state'] == 'working':
                        return account['id']
            else:
                print(resp)
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
            params = self._set_params('POST', 'api.huobi.pro', '/v1/order/orders/place', params)

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
            params = self._set_params('POST', 'api.huobi.pro', f'/v1/order/orders/{order_id}/submitcancel')

            resp = requests.post(url, params=params).json()
            data = False
            if resp['status'] == 'ok':
                data = True
                message = resp['status']
            else:
                message = resp['err-msg']
            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
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
            params = self._set_params('POST', 'api.huobi.pro', '/v1/order/orders/batchCancelOpenOrders', params)

            resp = requests.post(url, data=params, headers={'Content-Type': 'application/json'}).json()
            data = False
            if resp['status'] == 'ok' and resp['data']['failed-count'] == 0:
                data = True
                message = resp['status']
            else:
                message = resp['err-msg']
            info = {
                'func_name': 'cancel_all',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Huobi auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = self.order_list(symbol, limit=500)
            return orders
        except Exception as e:
            print(f'Huobi auth open orders error: {e}')

    def order_list(self, symbol: str, status: list = None, offset=1, limit=100):
        if status is None:
            status = ['created', 'partial-filled']
        try:
            url = self.urlbase + '/v1/order/openOrders'
            params = {
                'account-id': self._account_id(),
                'symbol': self._symbol_convert(symbol),
                'size': limit
            }
            params = self._set_params('GET', 'api.huobi.pro', '/v1/order/openOrders', params)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            results = []
            if resp['status'] == 'ok':
                for order in resp['data']:
                    if order['state'] in status:
                        results.append({
                            'order_id': order['id'],
                            'symbol': order['symbol'],
                            'side': order['type'].split('-')[0],
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
            params = self._set_params('GET', 'api.huobi.pro', f'/v1/order/orders/{order_id}')

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            order_detail = {}
            if resp['status'] == 'ok':
                order = resp['data']
                order_detail = {
                    'order_id': order_id,
                    'symbol': order['symbol'],
                    'side': order['type'].split('-')[0],
                    'price': float(order['price']),
                    'amount': float(order['amount']),
                    'price_avg': None,
                    'filled_amount': float(order['field-amount']),
                    'status': order['state'],
                    'create_time': round(order['created-at'] / 1000)
                }
                message = 'ok'
            else:
                message = resp["err-msg"]
                print(f'Huobi auth order detail error: {message}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': message,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Huobi auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + f'/v1/order/matchresults'
            params = {
                'symbol': self._symbol_convert(symbol),
                'size': limit
            }
            params = self._set_params('GET', 'api.huobi.pro', '/v1/order/matchresults', params)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            trades = []
            if resp['status'] == 'ok':
                for trade in resp['data']:
                    trades.append({
                        'detail_id': trade['trade-id'],
                        'order_id': trade['order-id'],
                        'symbol': symbol,
                        'create_time': round(trade['created-at'] / 1000),
                        'side': trade['type'].split('-')[0],
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'size': float(trade['filled-amount']),
                        'fees': float(trade['filled-fees']),
                        'fee_coin_name': None,
                        'exec_type': 'T' if trade['role'] == 'taker' else 'M'
                    })
            else:
                print(f'Huobi auth user trades error: {resp["err-msg"]}')
            return trades
        except Exception as e:
            print(f'Huobi auth user trades error: {e}')

    def wallet_balance(self):
        try:
            account_id = self._account_id()
            url = self.urlbase + f'/v1/account/accounts/{account_id}/balance'
            params = self._set_params('GET', 'api.huobi.pro', f'/v1/account/accounts/{account_id}/balance')

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/json'}).json()
            balance, frozen = {}, {}
            if resp['status'] == 'ok':
                for currency in resp['data']['list']:
                    if currency['type'] == 'trade':
                        balance[currency['currency']] = currency['balance']
                    if currency['type'] == 'frozen':
                        frozen[currency['currency']] = currency['balance']
            else:
                print(f'Huobi auth wallet balance error: {resp["err-msg"]}')
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
    # print(huo.user_trades('EOS_USDT'))
    # print(huo.wallet_balance())

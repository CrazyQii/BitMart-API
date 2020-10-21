import requests
import os
import json
import hmac
import hashlib
import time


class GateioAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, method, path, params=None, body=None):
        try:
            timestamp = str(int(time.time()))
            paramStr = ''
            if params is not None:
                paramStr += '&'.join([f'{key}={value}' for key, value in params.items()])

            if body is None:
                body = ''
            m = hashlib.sha512()
            m.update(body.encode('utf-8'))
            body = m.hexdigest()

            # Hash All
            signStr = f'{method.upper()}\n{path}\n{paramStr}\n{body}\n{timestamp}'

            sign = hmac.new(bytes(self.api_secret, encoding='utf-8'),
                            bytes(signStr,encoding='utf-8'), hashlib.sha512).hexdigest()
            return {
                'KEY': self.api_secret, 'Timestamp': timestamp, 'SIGN': sign
            }
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/spot/orders'
            params = {
                'currency_pair': symbol,
                'type': 'limit',
                'account': 'spot',
                'side': side,
                'amount': amount,
                'price': price,
                'time_in_force': 'gtc'
            }
            headers = self._sign_message('POST', '/api/v4/spot/orders', body=json.dumps(params))
            headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })

            resp = requests.post(url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:
                return resp.json()['id']
            else:
                print(f'Gateio auth error: {resp.json()["label"]}')
                return None
        except Exception as e:
            print(f'Gateio auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/spot/orders/{order_id}'
            params = {
                'currency_pair': symbol,
                'order_id': order_id
            }
            headers = self._sign_message('DELTE', f'/spot/orders/{order_id}', params=params)
            headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })

            resp = requests.delete(url, params=params, headers=headers)
            data = False
            if resp.status_code == 200:
                data = True
                message = resp.json()['label']
            else:
                message = resp.json()['label']
                print(f'Gateio auth error: {resp.json()["label"]}')

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Gateio auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            url = self.urlbase + f'/spot/orders'
            params = {
                'currency_pair': symbol,
                'side': side
            }
            headers = self._sign_message('DELTE', '/spot/orders/', params=params)
            headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })

            resp = requests.delete(url, params=params, headers=headers)
            data = False
            if resp.status_code == 200:
                data = True
                message = resp.json()['label']
            else:
                message = resp.json()['label']
                print(f'Gateio auth error: {resp.json()["label"]}')

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Gateio auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        try:
            url = self.urlbase + '/spot/open_orders'
            params = {
                'limit': limit
            }
            headers = self._sign_message('GET', '/spot/open_orders', params=params)
            headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })

            resp = requests.get(url, params=params, headers=headers)
            results = []
            if resp.status_code == 200:
                for order in resp.json()['orders']:
                    if order['currency_pair'] == symbol:
                        results.append({
                            'order_id': order['id'],
                            'symbol': order['currency_pair'],
                            'amount': float(order['size']),
                            'price': float(order['price']),
                            'side': order['side'],
                            'price_avg': None,
                            'filled_amount': float(order['amount']) - float(order['left']),
                            'create_time': order['create_time']
                        })
            else:
                print(f'Gateio auth error: {resp.json()["label"]}')
            return results
        except Exception as e:
            print(f'Gateio auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/spot/orders/{order_id}'
            params = {
                'order_id': order_id,
                'currency_pair': symbol
            }
            headers = self._sign_message('GET', f'/spot/orders/{order_id}', params=params)
            headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })

            resp = requests.get(url, params=params, headers=headers)
            order_detail = {}
            if resp.status_code == 200:
                order = resp.json()
                order_detail = {
                    'order_id': order['id'],
                    'symbol': order['currency_pair'],
                    'amount': float(order['size']),
                    'price': float(order['price']),
                    'side': order['side'],
                    'price_avg': None,
                    'filled_amount': float(order['amount']) - float(order['left']),
                    'create_time': order['create_time']
                }
            else:
                print(f'Gateio auth error: {resp.json()["label"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp.json()['label'],
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Gateio auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/spot/accounts'

            headers = self._sign_message('GET', f'/spot/accounts')
            headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })

            resp = requests.get(url, headers=headers)
            balance, frozen = {}, {}
            if resp.status_code == 200:
                wallet = resp.json()
                balance = {row['currency']: float(row['available']) for row in wallet}
                frozen = {row['currency']: float(row['locked']) for row in wallet}
            else:
                print(f'Gateio auth error: {resp.json()["label"]}')
            return balance, frozen
        except Exception as e:
            print(f'Gateio auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    # 需要实名认证才可测试
    gate = GateioAuth('https://api.gateio.ws/api/v4', 'ba47113fb14439d35d387c13ca015389', 'a0a4787803bf0734dc9ee722d1f86394df99f677a1665a7b43ae35439c86c1f8')
    # print(gate.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(gate.order_detail('BTC_USDT', '1'))
    # print(gate.open_orders('BTC_USDT'))
    # print(gate.cancel_order('UMA_USDT', '1'))
    # print(gate.cancel_all('BTC_USDT', 'buy'))
    # print(gate.wallet_balance())
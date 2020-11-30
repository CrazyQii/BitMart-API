import requests
import json
import hmac
import hashlib
import time
from urllib.parse import urlencode


class GateioAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_message(self, method, path, params=None, body=None):
        try:
            timestamp = str(int(time.time()))
            if params is None:
                params = ''
            else:
                params = urlencode(params)
            if body is None:
                body = ''

            m = hashlib.sha512()
            m.update(body.encode('utf-8'))
            body = m.hexdigest()

            # Hash All
            signStr = f'{method.upper()}\n{path}\n{params}\n{body}\n{timestamp}'

            sign = hmac.new(bytes(self.api_secret, encoding='utf-8'),
                            bytes(signStr, encoding='utf-8'), hashlib.sha512).hexdigest()
            return {
                'KEY': self.api_secret, 'Timestamp': timestamp, 'SIGN': sign
            }
        except Exception as e:
            print(e)

    def get_header(self, method, path, params=None):
        if method == 'POST':
            headers = self._sign_message(method, path, body=json.dumps(params))
        else:
            headers = self._sign_message(method, path, params=params)
        headers.update({
            'Content-type': 'application/json',
            'Accept': 'application/json',
        })
        return headers

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

            headers = self.get_header('POST', '/api/v4/spot/orders', params)
            resp = requests.post(url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:
                return resp.json()['id']
            else:
                print(f'Gateio auth place order error: {resp.json()}')
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
            headers = self.get_header('DELETE', f'/spot/orders/{order_id}', params)

            resp = requests.delete(url, params=params, headers=headers)
            data = False
            if resp.status_code == 200:
                data = True
                message = resp.json()['label']  # 无法判断返回格式
            else:
                message = resp.json()['label']
                print(f'Gateio auth error: {resp.json()}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Gateio auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                info = {
                    "func_name": "cancel_order",
                    "message": 'Empty orders',
                    "data": False
                }
                return info

            order_ids = []
            for order in orders:
                if order['type'] == side:
                    order_ids.append(order['order_id'])
            url = self.urlbase + '/spot/cancel_batch_orders'
            params = {
                'body': order_ids
            }
            headers = self.get_header('DELETE', '/spot/cancel_batch_orders', params=params)

            resp = requests.delete(url, params=params, headers=headers)
            data = False
            if resp.status_code == 200:
                data = True
                message = resp.json()
            else:
                message = resp.json()
                print(f'Gateio auth cancel order error: {message}')

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Gateio auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, offset=page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print(f'Gateio auth open orders error: {e}')

    def order_list(self, symbol: str, status=None, offset=1, limit=100):
        if status is None:
            status = ['open']
        try:
            url = self.urlbase + '/spot/open_orders'
            params = {
                'page': offset,
                'limit': limit
            }
            headers = self.get_header('GET', '/spot/open_orders', params=params)

            resp = requests.get(url, params=params, headers=headers)
            results = []
            if resp.status_code == 200:
                for pair in resp.json():
                    if pair['currency_pair'] == symbol:
                        for order in pair['orders']:
                            if order['status'] in status:
                                results.append({
                                    'order_id': order['id'],
                                    'symbol': order['currency_pair'],
                                    'amount': float(order['amount']),
                                    'price': float(order['price']),
                                    'side': order['side'],
                                    'price_avg': None,
                                    'filled_amount': float(order['amount']) - float(order['left']),
                                    'create_time': order['create_time']
                                })
            else:
                print(f'Gateio auth open orders error: {resp.json()}')
            return results
        except Exception as e:
            print(f'Gateio auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/spot/orders/{order_id}'
            params = {
                'order_id': order_id,
                'currency_pair': symbol
            }
            headers = self.get_header('GET', f'/spot/orders/{order_id}', params=params)

            resp = requests.get(url, params=params, headers=headers)
            order_detail = {}
            if resp.status_code == 200:
                order = resp.json()
                order_detail = {
                    'order_id': order['id'],
                    'symbol': order['currency_pair'],
                    'amount': float(order['amount']),
                    'price': float(order['price']),
                    'side': order['side'],
                    'price_avg': None,
                    'filled_amount': float(order['amount']) - float(order['left']),
                    'create_time': order['create_time']
                }
            else:
                print(f'Gateio auth order detail error: {resp.json()}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp.json(),
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Gateio auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/spot/my_trades'
            params = {'currency_pair': symbol, 'limit': limit, 'page': offset}
            headers = self.get_header('GET', '/spot/my_trades', params=params)

            resp = requests.get(url, params=params, headers=headers)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'detail_id': trade['id'],
                        'order_id': trade['order_id'],
                        'symbol': symbol,
                        'create_time': trade['create_time'],
                        'side': trade['side'],
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'size': float(trade['amount']),
                        'fees': float(trade['fee']),
                        'fee_coin_name': trade['fee_currency'],
                        'exec_type': 'M' if trade['role'] == 'maker' else 'T'
                    })
            else:
                print(f'Gateio auth user trades error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'Gateio auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/spot/accounts'
            headers = self.get_header('GET', f'/spot/accounts')

            resp = requests.get(url, headers=headers)
            balance, frozen = {}, {}
            if resp.status_code == 200:
                wallet = resp.json()
                balance = {row['currency']: float(row['available']) for row in wallet}
                frozen = {row['currency']: float(row['locked']) for row in wallet}
            else:
                print(f'Gateio auth wallet balance error: {resp.json()}')
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
    # print(gate.user_trades('BTC_USDT'))
    # print(gate.wallet_balance())
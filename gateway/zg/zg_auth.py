import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode


class ZGAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_'))

    def _sign_message(self, params):
        """ authtication """
        try:
            # signature string
            query = urlencode(params)
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(query, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        if side not in ['buy', 'sell']:
            print('side is wrong')
            return None
        try:
            url = self.urlbase + '/openapi/v1/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'side': side.upper(),
                'timeInForce': 'GTC',
                'type': 'LIMIT',
                'price': price,
                'quantity': amount,
                'timestamp': int(time.time() * 1000)
            }
            sign = self._sign_message(params)
            params['signature'] = sign
            headers = {'X-BH-APIKEY': self.api_key, 'Content-type': 'application/x-www-form-urlencoded'}
            resp = requests.post(url, data=params, headers=headers)
            if resp.status_code == 200:
                resp = resp.json()
                return resp
            else:
                print(f'ZG auth place order error: {resp.json()}')
                return None
        except Exception as e:
            print(f'ZG auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/openapi/v1/order'
            params = {
                'order_id': order_id,
                'timestamp': int(time.time())
            }
            sign = self._sign_message(params)
            params['signature'] = sign
            headers = {'X-BH-APIKEY': self.api_key, 'Content-type': 'application/x-www-form-urlencoded'}

            resp = requests.delete(url, data=params, headers=headers)
            data = False
            if resp.status_code == 200:
                resp = resp.json()
                data = resp['data']
                message = resp
            else:
                message = resp.json()
                print(f'ZG auth error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'ZG auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            # verify request error
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_order',
                    'message': 'orders are empty',
                    'data': True
                }

            for order in orders:
                if str(order['side']).lower() == side:
                    self.cancel_order(symbol, order['orderId'])
            info = {
                'func_name': 'cancel_order',
                'message': 'OK',
                'data': True
            }
            return info
        except Exception as e:
            print(f'ZG auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        try:
            url = self.urlbase + f'/openapi/v1/openOrders'
            params = {
                'symbol': self._symbol_convert(symbol),
                'limit': limit,
                'timestamp': int(time.time())
            }
            sign = self._sign_message(params)
            params['signature'] = sign
            headers = {'X-BH-APIKEY': self.api_key, 'Content-type': 'application/x-www-form-urlencoded'}
            resp = requests.get(url, params=params, headers=headers)
            results = []
            if resp.status_code == 200:
                resp = resp.json()
                for order in resp:
                    results.append({
                        'order_id': order['orderId'],
                        'symbol': order['symbol'],
                        'amount': float(order['origQty']),
                        'price': float(order['price']),
                        'side': order['side'],
                        'price_avg': None,
                        'filled_amount': float(order['executedQty']),
                        'create_time': int(order['time'] / 1000)
                    })
            else:
                print(f'ZG auth open order error: {resp}')
            return results
        except Exception as e:
            print(f'ZG auth open order error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/openapi/v1/myTrades'
            params = {'symbol': symbol, 'limit': limit, 'offset': offset, 'timestamp': int(time.time())}
            sign = self._sign_message(params)
            params['signature'] = sign
            headers = {'X-BH-APIKEY': self.api_key, 'Content-type': 'application/x-www-form-urlencoded'}

            resp = requests.get(url, params=params, headers=headers)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'detail_id': trade['id'],
                        'order_id': trade['orderId'],
                        'symbol': symbol,
                        'create_time': int(trade['time'] / 1000),
                        'side': 'buy' if trade['isBuyer'] else 'sell',
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'size': float(trade['qty']),
                        'fees': float(trade['commission']),
                        'fee_coin_name': trade['commissionAsset'],
                        'exec_type': 'M' if trade['isMaker'] else 'T'
                    })
            else:
                print(f'ZG auth user trades error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'ZG auth user trades error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/openapi/v1/order'
            params = {
                'orderId': order_id,
                'timestamp': int(time.time())
            }
            sign = self._sign_message(params)
            params['signature'] = sign
            headers = {'X-BH-APIKEY': self.api_key, 'Content-type': 'application/x-www-form-urlencoded'}

            resp = requests.get(url, params=params, headers=headers)
            order_detail = {}
            if resp.status_code == 200:
                content = resp.json()
                order_detail = {
                    'order_id': content['orderId'],
                    'symbol': symbol,
                    'side': content['side'],
                    'price': float(content['price']),
                    'amount': float(content['origQty']),
                    'price_avg': None,
                    'filled_amount': float(content['executedQty']),
                    'create_time': int(content['time']/1000)
                }
            else:
                print(f'ZG auth order detail error: {resp.json()}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp.json(),
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'ZG auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/openapi/v1/account'
            params = {'timestamp': int(time.time())}
            sign = self._sign_message(params)
            params['signature'] = sign
            headers = {'X-BH-APIKEY': self.api_key, 'Content-type': 'application/x-www-form-urlencoded'}
            resp = requests.get(url, params=params, headers=headers)
            balance, frozen = {}, {}
            if resp.status_code == 200:
                resp = resp.json()
                wallet = resp["balances"]
                balance = {row["asset"]: float(row["free"]) for row in wallet}
                frozen = {row["asset"]: float(row["locked"]) for row in wallet}
            else:
                print(f'ZG auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'ZG auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = ZGAuth('https://api.zg.com', 'BjlZajZl98KMntTgp02hUs044VFqPVeVDcPfTZFW08EhXH3268cNlH9Z1jpNyKMw', '9lWOMaJxOh3K28qtZtcbep5UAijZd3sU5S8RjK4tQcKmQBhLZRW3Yc05VYvuo4L3', 'mock')
    print(bit.place_order('BTC_USDT', 1.0016, 11, 'buy'))
    print(bit.order_detail('BTC_USDT', '1'))
    print(bit.open_orders('BTC_USDT'))
    print(bit.cancel_order('UMA_USDT', '1'))
    print(bit.cancel_all('BTC_USDT', 'buy'))
    print(bit.user_trades('BTC_USDT'))
    print(bit.wallet_balance())

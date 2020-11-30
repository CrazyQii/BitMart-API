import requests
import hmac
import hashlib
import time
import os
import operator
from urllib.parse import urlencode

cur_path = os.path.abspath(os.path.dirname(__file__))


class WootradeAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _symbol_convert(self, symbol: str):
        return "SPOT_" + symbol

    def _sign_message(self, ts, params=None):
        try:
            if params is not None:
                sort = sorted(params.items(), key=operator.itemgetter(0))
            else:
                sort = ''
            msg = urlencode(sort)
            msg += '|' + ts
            return hmac.new(self.api_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
        except Exception as e:
            print(e)

    def get_headers(self, ts, sign):
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "x-api-key": self.api_key,
                   "x-api-signature": sign,
                   "x-api-timestamp": ts,
                   "cache-control": "no-cache"}
        return headers

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/v1/order'
            ts = str(time.time()*1000)
            params = dict()
            params['symbol'] = self._symbol_convert(symbol)
            params['order_quantity'] = amount
            params['order_price'] = price
            params['side'] = side.upper()
            params['order_type'] = 'LIMIT'

            sign = self._sign_message(ts, params)
            headers = self.get_headers(ts, sign)
            resp = requests.post(url, data=params, headers=headers).json()
            if resp['success']:
                return resp['order_id']
            else:
                print(f'Wootrade auth place order error: {resp}')
                return None
        except Exception as e:
            print(f'Wootrade auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/v1/order'
            ts = str(time.time())
            params = dict()
            params['symbol'] = self._symbol_convert(symbol)
            params['order_id'] = order_id
            sign = self._sign_message(ts, params)
            headers = self.get_headers(ts, sign)
            resp = requests.delete(url, params=params, headers=headers).json()
            data = False
            if resp['success']:
                data = resp['success']
                message = resp
            else:
                message = resp
                print(f'Wootrade auth cancel order error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Wootrade auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_order',
                    'message': 'Empty orders',
                    'data': False
                }

            for order in orders:
                if str(order['side']).lower() == side:
                    self.cancel_order(symbol, order['order_id'])
            info = {
                'func_name': 'cancel_order',
                'message': 'OK',
                'data': True
            }
            return info
        except Exception as e:
            print(f'Wootrade auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, offset=page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print(f'Wootrade auth open orders error: {e}')

    def order_list(self, symbol: str, status=None, offset=1, limit=100):
        if status is None:
            status = ['PARTIAL_FILLED']
        try:
            url = self.urlbase + '/v1/orders'
            ts = str(time.time())
            params = dict()
            params['symbol'] = self._symbol_convert(symbol),
            params['status'] = status
            params['page'] = offset
            sign = self._sign_message(ts, params)
            headers = self.get_headers(ts, sign)

            resp = requests.get(url, params=params, headers=headers).json()
            results = []
            if resp['success']:
                for order in resp['rows']:
                    results.append({
                        'order_id': order['order_id'],
                        'symbol': symbol,
                        'side': order['side'].lower(),
                        'price': float(order['price']),
                        'amount': float(order['quantity']),
                        'price_avg': None,
                        'filled_amount': float(order['executed']),
                        'create_time': round(order['create_time'])
                    })
            else:
                print(f'Wootrade auth open orders error: {resp}')
            return results
        except Exception as e:
            print(f'Wootrade auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/v1/order/order_id'
            ts = str(time.time())

            sign = self._sign_message(ts)
            headers = self.get_headers(ts, sign)
            resp = requests.get(url, headers=headers).json()
            order_detail = {}
            if resp['success']:
                order_detail = {
                    'order_id': resp['order_id'],
                    'symbol': symbol,
                    'amount': float(resp['quantity']),
                    'price': float(resp['price']),
                    'side': resp['side'].lower(),
                    'price_avg': None,
                    'filled_amount': float(resp['executed']),
                    'status': float(resp['status']),
                    'create_time': round(float(resp['created_time']))
                }
            else:
                print(f'Wootrade auth order detail error: {resp}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Wootrade auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/v1/client/trades'
            ts = str(time.time())
            params = dict()
            params['symbol'] = self._symbol_convert(symbol),
            params['page'] = offset

            sign = self._sign_message(ts, params)
            headers = self.get_headers(ts, sign)

            resp = requests.get(url, params=params, headers=headers).json()
            trades = []
            if resp['success']:
                i = 0
                for trade in resp['row']:
                    if i > limit:
                        break
                    trades.append({
                        'detail_id': trade['id'],
                        'order_id': trade['order_id'],
                        'symbol': symbol,
                        'create_time': round(trade['executed_timestamp']),
                        'side': trade['side'].lower(),
                        'price_avg': None,
                        'notional': float(trade['executed_price']),
                        'size': float(trade['executed_quantity']),
                        'fees': float(trade['fee']),
                        'fee_coin_name': trade['fee_asset'],
                        'exec_type': None
                    })
                    i = i + 1
            else:
                print(f'Wootrade auth user trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Wootrade auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/v2/client/holding'
            ts = str(int(time.time()))
            sign = self._sign_message(ts)
            headers = self.get_headers(ts, sign)
            resp = requests.get(url, headers=headers).json()
            balance, frozen = {}, {}
            if resp['success']:
                balance = {row["token"]: float(row["holding"]) for row in resp["holding"]}
                frozen = {row["token"]: float(row["frozen"]) for row in resp["holding"]}
            else:
                print(f'Wootrade auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Wootrade auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    woo = WootradeAuth('https://nexus.kronostoken.com', 'AbmyVJGUpN064ks5ELjLfA==', 'QHKRXHPAW1MC9YGZMAT8YDJG2HPR')
    # print(woo.place_order('BTC_USDT', 1.0016, 11, 'buy'))
    # print(woo.order_detail('BTC_USDT', '1'))
    # print(woo.open_orders('BTC_USDT'))
    # print(woo.cancel_order('BTC_USDT', '1'))
    # print(woo.cancel_all('BTC_USDT', 'buy'))
    # print(woo.user_trades('BTC_USDT'))
    # print(woo.wallet_balance())

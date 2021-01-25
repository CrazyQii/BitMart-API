import requests
import hashlib
import time
import operator
from urllib.parse import urlencode


class MxcAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _timetamp(self):
        return str(time.time())

    def _uts_to_ts(self, uts):
        timeArray = time.strptime(uts, '%Y-%m-%d %H:%M:%S')
        ts = time.mktime(timeArray)
        return ts

    def _sign_message(self, params):
        sort = sorted(params.items(), key=operator.itemgetter(0))
        msg = urlencode(sort) + f'&api_secret={self.api_secret}'
        sign = hashlib.md5(msg.encode('utf-8')).hexdigest()
        return sign

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/open/api/v1/private/order'
            params = {
                'api_key': self.api_key,
                'req_time': self._timetamp(),
                'market': symbol,
                'price': price,
                'quantity': amount,
                'trade_type': '1' if side == 'buy' else '2'
            }
            params['sign'] = self._sign_message(params)

            resp = requests.post(url, data=params).json()
            if resp['code'] == 200:
                return resp['data']
            else:
                print(f'Mxc auth place order error: {resp["msg"]}')
                return None
        except Exception as e:
            print(f'Mxc auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id):
        try:
            url = self.urlbase + '/open/api/v2/order/cancel'
            params = {
                'api_key': self.api_key,
                'req_time': self._timetamp(),
                'market': symbol,
                'trade_no': order_id
            }
            params['sign'] = self._sign_message(params)

            resp = requests.delete(url, params=params).json()
            data = False
            if resp['code'] == 200:
                data = True
                message = resp['msg']
            else:
                message = resp['msg']
                print(f'Mxc auth cancel error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Mxc auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        orders = self.open_orders(symbol)
        if len(orders) == 0:
            info = {
                'func_name': 'cancel_all',
                'message': 'Empty orders',
                'data': False
            }
            return info
        try:
            order_ids = []
            side = '1' if side == 'buy' else '2'
            for order in orders:
                if order['type'] == side:
                    order_ids.append(order['order_id'])
            url = self.urlbase + '/open/api/v1/private/order_cancel'
            params = {
                'api_key': self.api_key,
                'req_time': self._timetamp(),
                'market': symbol,
                'trade_no': order_ids
            }
            params['sign'] = self._sign_message(params)

            resp = requests.post(url, data=params).json()
            data = False
            if resp['code'] == 200:
                data = True
                message = resp['msg']
            else:
                message = resp['msg']
                print(f'Mxc auth cancel error: {message}')
            info = {
                'func_name': 'cancel_all',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Mxc auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, offset=page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print(f'Mxc auth open orders error: {e}')

    def order_list(self, symbol: str, status=None, offset=1, limit=100):
        if status is None:
            status = ['1', '2', '3']
        try:
            url = self.urlbase + '/open/api/v1/private/current/orders'
            params = {
                'api_key': self.api_key,
                'req_time': self._timetamp(),
                'market': symbol,
                'page_num': offset,
                'page_size': limit
            }
            params['sign'] = self._sign_message(params)

            resp = requests.get(url, params=params).json()
            results = []
            if resp['code'] == 200:
                for order in resp['data']:
                    if order['status'] in status:
                        results.append({
                            'order_id': order['id'],
                            'symbol': symbol,
                            'side': 'buy' if order['type'] == '1' else 'sell',
                            'price': float(order['price']),
                            'amount': float(order['totalQuantity']),
                            'price_avg': None,
                            'filled_amount': float(order['tradedQuantity']),
                            'create_time': self._uts_to_ts(order['createTime'])
                        })
            else:
                print(f'Mxc auth open orders error: {resp["msg"]}')
            return results
        except Exception as e:
            print(f'Mxc auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/open/api/v1/private/order'
            params = {
                'api_key': self.api_key,
                'req_time': self._timetamp(),
                'market': symbol,
                'trade_no': order_id
            }
            params['sign'] = self._sign_message(params)

            resp = requests.get(url, params=params).json()
            order_detail = {}
            if resp['code'] == 200:
                content = resp['data']
                if content is not None:
                    order_detail = {
                        'order_id': content['id'],
                        'symbol': symbol,
                        'side': 'buy' if content['type'] == 1 else 'sell',
                        'price': float(content['price']),
                        'amount': float(content['totalQuantity']),
                        'price_avg': None,
                        'filled_amount': float(content['tradedQuantity']),
                        'status': content['status'],
                        'create_time': self._uts_to_ts(content['createTime'])
                    }
            else:
                print(f'Mxc auth order detail error: {resp["msg"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp['msg'],
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Mxc auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/open/api/v1/private/orders'
            params = {
                'api_key': self.api_key,
                'req_time': int(time.time()),
                'market': symbol,
                'page_num': offset,
                'page_size': limit
            }
            params['sign'] = self._sign_message(params)

            resp = requests.get(url, params=params).json()
            trades = []
            if resp['code'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': None,
                        'order_id': trade['id'],
                        'symbol': symbol,
                        'create_time': self._uts_to_ts(trade['createTime']),
                        'side': 'buy' if trade['type'] == 1 else 'sell',
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'size': float(trade['totalQuantity']),
                        'fees': None,
                        'fee_coin_name': None,
                        'exec_type': None
                    })
            else:
                print(f'Mxc auth user trades error: {resp["msg"]}')
            return trades
        except Exception as e:
            print(f'Mxc auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/open/api/v1/private/account/info'
            params = {
                'api_key': self.api_key,
                'req_time': self._timetamp()
            }
            params['sign'] = self._sign_message(params)

            resp = requests.get(url, params=params)
            balance, frozen = {}, {}
            if resp.status_code == 200:
                wallet = resp.json()
                balance = {key: float(value['available']) for key, value in wallet.items()}
                frozen = {key: float(value['frozen']) for key, value in wallet.items()}
            else:
                print(f'Mxc auth wallet balance error: {resp.json()["msg"]}')
            return balance, frozen
        except Exception as e:
            print(f'Mxc auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    mxc = MxcAuth('https://www.mxcio.co', 'mx0Iw5GHIlySTepTAN', 'ec4f09f088d642d2b2ebfae695b9c511')
    # print(mxc.place_order('BTC_USDT', 1.0016, 11, 'buy'))
    # print(mxc.order_detail('BTC_USDT', '1'))
    # print(mxc.open_orders('BTC_USDT'))
    # print(mxc.cancel_order('BTC_USDT', '1'))
    # print(mxc.cancel_all('BTC_USDT', 'buy'))
    # print(mxc.user_trades('BTC_USDT'))
    # print(mxc.wallet_balance())

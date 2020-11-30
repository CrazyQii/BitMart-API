import requests
import hmac
import hashlib
import time
import operator
from urllib.parse import urlencode


class MxcAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, method, path, params):
        if method == 'POST':
            paramStr = dict()
            paramStr['api_key'] = self.api_key
            paramStr['req_time'] = int(time.time())
            msg = f'{method}\n{path}\n{urlencode(paramStr)}'
        else:
            sort = sorted(params.items(), key=operator.itemgetter(0))
            msg = f'{method}\n{path}\n{urlencode(sort)}'
        sign = hmac.new(bytes(self.api_secret, encoding='utf-8'),
                        bytes(msg, encoding='utf-8'), hashlib.sha256).hexdigest()
        return sign

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/open/api/v2/order/place'
            params = {
                'api_key': self.api_key,
                'req_time': str(int(time.time())),
                'symbol': symbol,
                'price': price,
                'quantity': amount,
                'trade_type': 'BID' if side == 'buy' else 'ASK',
                'order_type': 'LIMIT_ORDER'
            }
            sign = self._sign_message('POST', '/open/api/v2/order/place', params)
            params['sign'] = sign

            resp = requests.post(url, data=params).json()
            if resp['code'] == 200:
                print(resp)
            else:
                print(f'Mxc auth error: {resp}')
                return None
        except Exception as e:
            print(f'Mxc auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id):
        try:
            url = self.urlbase + '/open/api/v2/order/cancel'
            params = {
                'api_key': self.api_key,
                'req_time': str(int(time.time())),
                'order_ids': order_id
            }
            sign = self._sign_message('DELETE', '/open/api/v2/order/cancel', params)
            params['sign'] = sign

            resp = requests.delete(url, params=params).json()
            data = False
            if resp['code'] == 200:
                data = resp['data']
                message = resp
            else:
                message = resp
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
            side = 'ASK' if side == 'sell' else 'BID'
            for order in orders:
                if order['type'] == side:
                    order_ids.append(order['order_id'])

            result = self.cancel_order(symbol, order_ids)
            info = {
                'func_name': 'cancel_order',
                'message': 'OK',
                'data': result['data']
            }
            return info
        except Exception as e:
            print(f'Mxc auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = self.order_list(symbol, limit=500)
            return orders
        except Exception as e:
            print(f'Mxc auth open orders error: {e}')

    def order_list(self, symbol: str, status=None, offset=1, limit=100):
        if status is None:
            status = ['PARTIALLY_FILLED']
        try:
            url = self.urlbase + '/open/api/v2/order/open_orders'
            params = {
                'api_key': self.api_key,
                'req_time': int(time.time()),
                'symbol': symbol,
                'limit': limit
            }
            sign = self._sign_message('GET', '/open/api/v2/order/open_orders', params)
            params['sign'] = sign

            resp = requests.get(url, params=params).json()
            results = []
            if resp['code'] == 200:
                for order in resp['data']:
                    if order['state'] in status:
                        results.append({
                            'order_id': order['id'],
                            'symbol': order['symbol'],
                            'side': 'sell' if order['trade_type'] == 'ASK' else 'buy',
                            'price': float(order['price']),
                            'amount': float(order['quantity']),
                            'price_avg': None,
                            'filled_amount': float(order['amount']),
                            'create_time': round(order['create_time'] / 1000)
                        })
            else:
                print(f'Mxc auth open orders error: {resp}')
            return results
        except Exception as e:
            print(f'Mxc auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/open/api/v2/order/query'
            params = {
                'api_key': self.api_key,
                'req_time': int(time.time()),
                'order_ids': order_id
            }
            sign = self._sign_message('GET', '/open/api/v2/order/query', params)
            params['sign'] = sign

            resp = requests.get(url, params=params).json()
            order_detail = {}
            if resp['code'] == 200 and len(resp['data']) > 0:
                content = resp['data'][0]
                order_detail = {
                    'order_id': content['id'],
                    'symbol': content['symbol'],
                    'side': 'sell' if content['trade_type'] == 'ASK' else 'buy',
                    'price': float(content['price']),
                    'amount': float(content['quantity']),
                    'price_avg': None,
                    'filled_amount': float(content['deal_quantity']),
                    'status': float(content['status']),
                    'create_time': round(content['create_time'] / 1000)
                }
            else:
                print(f'Mxc auth order detail error: {resp}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Mxc auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/open/api/v2/order/deals'
            params = {
                'api_key': self.api_key,
                'req_time': int(time.time()),
                'symbol': symbol,
                'limit': limit
            }
            sign = self._sign_message('GET', '/open/api/v2/order/deals', params)
            params['sign'] = sign

            resp = requests.get(url, params=params).json()
            trades = []
            if resp['code'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': None,
                        'order_id': trade['order_id'],
                        'symbol': symbol,
                        'create_time': round(trade['create_time'] / 1000),
                        'side': 'buy' if trade['trade_type'] == 'BID' else 'sell',
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'size': float(trade['quantity']),
                        'fees': float(trade['fee']),
                        'fee_coin_name': trade['fee_currency'],
                        'exec_type': 'T' if trade['is_taker'] else 'M'
                    })
            else:
                print(f'Mxc auth user trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Mxc auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/open/api/v2/account/info'
            params = dict()
            params['api_key'] = self.api_key
            params['req_time'] = int(time.time())
            sign = self._sign_message('GET', '/open/api/v2/account/info', params)
            params['sign'] = sign

            resp = requests.get(url, params=params).json()
            balance, frozen = {}, {}
            if resp['code'] == 200:
                wallet = resp['data']
                balance = {key: float(value['available']) for key, value in wallet.items()}
                frozen = {key: float(value['frozen']) for key, value in wallet.items()}
            else:
                print(f'Mxc auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Mxc auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    mxc = MxcAuth('https://www.mxcio.co', 'mx0Iw5GHIlySTepTAN', 'ec4f09f088d642d2b2ebfae695b9c511')
    # print(mxc.place_order('BTC_USDT', 1.0016, 11, 'buy'))  # 认证失败
    # print(mxc.order_detail('BTC_USDT', '1'))
    # print(mxc.open_orders('BTC_USDT'))
    print(mxc.cancel_order('BTC_USDT', '1'))
    print(mxc.cancel_all('BTC_USDT', 'buy'))
    # print(mxc.user_trades('BTC_USDT'))
    # print(mxc.wallet_balance())
import hmac
import hashlib
import time
import json
import requests


class VinexAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_message(self, query):
        try:
            msg = ''
            # signature string
            for key in sorted(query.keys()):
                msg += '_' + str(query[key])
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(msg[1:], encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def _request(self, method: str, url: str, params: dict):
        try:
            headers = {
                'api-key': self.api_key,
                'signature': self._sign_message(params)
            }
            if method == 'POST':
                resp = requests.post(url, data=params, headers=headers).json()
            else:
                resp = requests.get(url, params=params, headers=headers).json()
            return resp
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        if side not in ['buy', 'sell']:
            print('side is wrong')
            return None
        try:
            url = self.urlbase + '/api/v2/place-order'
            params = {
                'market': symbol,
                'type': 'SELL' if side == 'sell' else 'BUY',
                'order_type': 'LIMIT',
                'price': price,
                'amount': amount,
                'time_stamp': str(time.time())
            }
            resp = self._request('POST', url, params)
            if 'status' in resp and resp['status'] == 200:
                return resp['data']['uid']  # 未在response中找到对应order_id
            else:
                print(f'Vinex auth place order error: {resp}')
                return None
        except Exception as e:
            print(f'Vinex auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/api/v2/cancel-order'
            params = {
                'market': symbol,
                'uid': order_id,
                'time_stamp': str(time.time())
            }
            resp = self._request('POST', url, params)
            data = False
            if 'status' in resp and resp['status'] == 200:
                data = True
                message = resp['message']
            else:
                message = resp
                print(f'Vinex auth cancel order error: {message}')
            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Vinex auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_all',
                    'message': 'Empty order',
                    'data': False
                }

            data = True
            for order in orders:
                if str(order['side']).lower() == side:
                    result = self.cancel_order(symbol, order['order_id'])['data']
                    if result is False:
                        data = False
            info = {
                'func_name': 'cancel_all',
                'message': 'OK',
                'data': data
            }
            return info

        except Exception as e:
            print(f'Vinex auth cancel all error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, 10, page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print(f'Vinex auth open orders error: {e}')

    def order_list(self, symbol: str, status=10, offset=1, limit=100):
        try:
            url = self.urlbase + '/api/v2/get-my-orders'
            params = {
                'market': symbol,
                'status': status,  # 参数类型错误 FENDING = 10
                'page': offset,
                'limit': limit,
                'time_stamp': str(time.time())
            }
            resp = self._request('GET', url, params)
            results = []
            if 'status' in resp and resp['status'] == 200:
                for order in resp['data']:
                    results.append({
                        'order_id': order['uid'],
                        'symbol': order['pairSymbol'],
                        'amount': float(order['amount']),
                        'price': float(order['price']),
                        'side': 'sell' if order['actionType'] == 0 else 'buy',
                        'price_avg': None,
                        'filled_amount': float(order['amount']) - float(order['remain']),
                        'create_time': order['createdAt']
                    })
            else:
                print(f'Vinex auth open order error: {resp}')
            return results
        except Exception as e:
            print(f'Vinex auth open order error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/api/v2/get-my-trading'
            params = {
                'market': symbol,
                'page': offset,
                'limit': limit,
                'time_stamp': str(time.time())
            }
            resp = self._request('GET', url, params)
            trades = []
            if 'status' in resp and resp['status'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': trade['id'],
                        'order_id': trade['orderId'],
                        'symbol': symbol,
                        'create_time': trade['createdAt'],
                        'side': 'sell' if trade['actionType'] == 0 else 'buy',
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'amount': float(trade['amount']),
                        'fees': float(trade['fee']),
                        'fee_coin_name': trade['feeAsset'],
                        'exec_type': None
                    })
            else:
                print(f'Vinex auth user trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Vinex auth user trades error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        pass

    def wallet_balance(self):
        try:
            url = self.urlbase + '/api/v2/balances'
            params = {'time_stamp': str(time.time())}
            resp = self._request('GET', url, params)
            balance, frozen = {}, {}
            if 'status' in resp and resp['status'] == 200:
                wallet = resp['data']
                balance = {row['asset']: float(row['free']) for row in wallet}
                frozen = {row['asset']: float(row['locked']) for row in wallet}
            else:
                print(f'Vinex auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Vinex auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = VinexAuth('https://api.vinex.network', 'uykusdqssu54ea88k1jxi04hubc5ev50', 'hfkwtnsst89yqah5vqy7yjqa7egyow5d')
    # print(bit.place_order('BTC_ETH', 1.0016, 11, 'buy'))
    # print(bit.order_detail('BTC_ETH', '1'))
    # print(bit.open_orders('BTC_ETH'))
    # print(bit.cancel_order('BTC_ETH', '1'))
    # print(bit.cancel_all('BTC_ETH', 'buy'))
    # print(bit.user_trades('BTC_ETH'))
    # print(bit.wallet_balance())

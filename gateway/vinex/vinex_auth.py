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
        self.memo = passphrase

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
                'time_stamp': int(time.time())
            }
            headers = {
                'api-key': self.api_key,
                'signature': self._sign_message(params)
            }
            resp = requests.post(url, data=params, headers=headers).json()
            if resp['status'] == 200:
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
                'time_stamp': int(time.time())
            }
            headers = {
                'api-key': self.api_key,
                'signature': self._sign_message(params)
            }

            resp = requests.post(url, data=params, headers=headers).json()
            data = False
            if resp['status'] == 200:
                data = resp['data']
                message = resp['message']
            else:
                message = resp['message']
                print(f'Vinex auth error: {message}')

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
                    'func_name': 'cancel_order',
                    'message': 'Vinex auth cancel order is empty',
                    'data': True
                }

            for order in orders:
                if str(order['order_side']) == side:
                    self.cancel_order(symbol, order['order_id'])
            info = {
                'func_name': 'cancel_order',
                'message': 'OK',
                'data': True
            }
            return info

        except Exception as e:
            print(f'Vinex auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=10, offset=1, limit=100):
        try:
            url = self.urlbase + f'/api/v2/get-my-orders'
            params = {
                'market': symbol,
                'status': str(status),
                'page': offset,
                'limit': limit,
                'time_stamp': int(time.time())
            }
            headers = {
                'api-key': self.api_key,
                'signature': self._sign_message(params)
            }
            resp = requests.get(url, params=params, headers=headers).json()
            results = []
            if resp['status'] == 200:
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
                'time_stamp': int(time.time())
            }
            headers = {
                'api-key': self.api_key,
                'signature': self._sign_message(params)
            }

            resp = requests.get(url, params=params, headers=headers).json()
            trades = []
            print(resp)
            if resp['status'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': trade['id'],
                        'order_id': trade['orderId'],
                        'symbol': symbol,
                        'create_time': int(trade['createdAt'] / 1000),
                        'side': 'sell' if trade['type'] == 0 else 'buy',
                        'price_avg': None,
                        'notional': float(trade['amount']) * float(trade['price']),
                        'size': float(trade['amount']),
                        'fees': float(trade['fee']),
                        'fee_coin_name': trade['feeAsset'],
                        'exec_type': trade['actionType']
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
            params = {'time_stamp': int(time.time())}
            headers = {
                'api-key': self.api_key,
                'signature': self._sign_message(params)
            }
            resp = requests.get(url, params=params, headers=headers).json()
            balance, frozen = {}, {}
            if resp['status'] == 200:
                wallet = resp["data"]
                balance = {row["asset"]: float(row["free"]) for row in wallet}
                frozen = {row["asset"]: float(row["locked"]) for row in wallet}
            else:
                print(f'Vinex auth wallet balance error: {resp["message"]}')
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

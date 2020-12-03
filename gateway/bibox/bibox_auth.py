import requests
import hmac
import hashlib
import json


class BiboxAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_message(self, cmd, body):
        try:
            param = [{'cmd': cmd, 'body': body}]
            sign = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(json.dumps(param), encoding='utf-8'),
                            hashlib.md5).hexdigest()
            return {
                'cmds': json.dumps(param),
                'apikey': self.api_key,
                'sign': sign
            }
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/v2/orderpending'
            params = {
                'pair': symbol,
                'account_type': 0,
                'order_side': 1 if side == 'buy' else 2,
                'order_type': 2,
                'price': price,
                'amount': amount
            }
            params = self._sign_message('orderpending/trade', params)

            resp = requests.post(url, data=params).json()
            if 'result' in resp['result'][0]:
                return resp['result']
            else:
                print(f'Bibox auth place order error: {resp["error"]["msg"]}')
        except Exception as e:
            print(f'Bibox auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/v1/orderpending'
            params = {
                'orders_id': order_id
            }

            params = self._sign_message('orderpending/cancelTrade', params)

            resp = requests.post(url, data=params).json()
            data = False
            if 'result' in resp['result'][0]:
                data = True
                message = resp['result'][0]['result']
            else:
                message = resp['error']['msg']
                print(f'Bibox auth cancel order error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Bibox auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            side = '1' if side == 'buy' else '2'
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_all',
                    'message': 'Empty order',
                    'data': True
                }

            data = True
            for order in orders:
                if str(order['side']) == side:
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
            print(f'Bibox auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, offset=page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print(f'Bibox auth open orders error: {e}')

    def order_list(self, symbol: str, status: list = None, offset=1, limit=50):
        if status is None:
            status = [1, 2]
        try:
            url = self.urlbase + '/v1/orderpending'
            params = {
                'pair': symbol,
                'account_type': 0,
                'page': offset,
                'size': limit
            }
            params = self._sign_message('orderpending/orderPendingList', params)

            resp = requests.post(url, data=params)
            results = []
            resp = resp.json()
            if 'result' in resp['result'][0]:
                for order in resp['result'][0]['result']['items']:
                    if order['status'] in status:
                        results.append({
                            'order_id': order['id'],
                            'symbol': symbol,
                            'amount': float(order['amount']),
                            'price': float(order['price']),
                            'side': order['side'],
                            'price_avg': None,
                            'filled_amount': float(order['deal_amount']),
                            'create_time': int(order['createdAt'] / 1000)
                        })
            else:
                print(f'Bibox auth open orders error: {resp["error"]["msg"]}')
            return results
        except Exception as e:
            print(f'Bibox auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/v1/orderpending'
            params = {
                'id': order_id,
                'account_type': 0,
            }
            params = self._sign_message('orderpending/order', params)

            resp = requests.post(url, data=params).json()
            order_detail = {}
            if 'result' in resp['result'][0]:
                content = resp['result'][0]['result']
                order_detail = {
                    'order_id': content['id'],
                    'symbol': symbol,
                    'amount': float(content['amount']),
                    'price': float(content['price']),
                    'side': 'buy' if content['order_side'] == 1 else 'sell',
                    'price_avg': None,
                    'filled_amount': float(content['deal_amount']),
                    'status': content['status'],
                    'create_time': round(content['createdAt'] / 1000)
                }
            else:
                print(f'Bibox auth order detail error: {resp["error"]["msg"]}')
            return order_detail
        except Exception as e:
            print(f'Bibox auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/v1/orderpending'
            params = {'pair': symbol, 'account_type': 0, 'id': '10000000000', 'page': offset}
            params = self._sign_message('orderpending/order', params)

            resp = requests.post(url, data=params).json()
            trades = []
            if 'result' in resp['result'][0]:
                content = resp['result'][0]['result']
                if 'items' in content:
                    i = 0
                    for trade in content['items']:
                        if i > limit:
                            break
                        trades.append({
                            'detail_id': trade['relay_id'],
                            'order_id': trade['id'],
                            'symbol': f'{trade["coin_symbol"]}_{trade["currency_symbol"]}',
                            'create_time': int(trade['createdAt'] / 1000),
                            'side': 'buy' if trade['order_side'] == 1 else 'sell',
                            'price_avg': None,
                            'notional': float(trade['price']),
                            'size': float(trade['amount']),
                            'fees': float(trade['fee']),
                            'fee_coin_name': trade['fee_symbol'],
                            'exec_type': 'M' if trade['is_maker'] == 1 else 'T',
                        })
                        i = i + 1
            else:
                print(f'Bibox auth user trades error: {resp["error"]["msg"]}')
            return trades
        except Exception as e:
            print(f'Bibox auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/v1/transfer'
            params = {'select': 1}
            params = self._sign_message('transfer/assets', params)

            resp = requests.post(url, data=params).json()
            balance, frozen = {}, {}
            if 'result' in resp['result'][0]:
                wallet = resp['result'][0]['result']['assets_list']
                balance = {row['coin_symbol']: float(row['balance']) for row in wallet}
                frozen = {row['coin_symbol']: float(row['freeze']) for row in wallet}
            else:
                print(f'Bibox auth wallet balance error: {resp["error"]["msg"]}')
            return balance, frozen
        except Exception as e:
            print(f'Bibox auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = BiboxAuth('https://api.bibox.com', '59ed9c456d6d1d5bc843ac2fde9fdbe34b820a89',
                    '851fdebdc8a40d20b70056d08e0dd3a2cbacc35d')
    # print(bit.place_order('BTC_USDT', 1.0016, 1.5, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('BTC_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.user_trades('BTC_USDT'))
    # print(bit.wallet_balance())

import requests
import hmac
import hashlib
import json


class BiboxAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, cmd, body):
        try:
            param = [{
                'cmd': cmd,
                'body': body
            }]
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

            resp = requests.post(url, data=params)
            resp = resp.json()
            if 'result' in resp['result'][0].keys():
                return resp.json()['result']
            else:
                print(f'Bibox auth error: {resp["result"][0]["error"]}')
                return None
        except Exception as e:
            print(f'Bibox auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/v1/orderpending'
            params = {
                'orders_id': order_id
            }

            params = self._sign_message('orderpending/cancelTrade', params)

            resp = requests.post(url, data=params)
            resp = resp.json()
            data = False
            if 'result' in resp['result'][0].keys():
                data = True
                message = resp['result'][0]['result']
            else:
                message = resp['result'][0]['error']
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
                    'func_name': 'cancel_order',
                    'message': 'Bibox auth cancel order is empty',
                    'data': False
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
            print(f'Bibox auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=1, offset=1, limit=100):
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
            if 'result' in resp['result'][0].keys():
                for order in resp['result'][0]['result']['items']:
                    if order['status'] == status or 0:
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
                print(f'Bibox auth open orders error: {resp["result"][0]["error"]}')
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

            resp = requests.post(url, data=params)
            order_detail = {}
            resp = resp.json()
            if 'result' in resp['result'][0]:
                content = resp['result'][0]['result']
                order_detail = {
                    'order_id': content['id'],
                    'symbol': symbol,
                    'amount': float(content['amount']),
                    'price': float(content['price']),
                    'side': content['side'],
                    'price_avg': None,
                    'filled_amount': float(content['deal_amount']),
                    'create_time': int(content['createdAt'] / 1000)
                }
            else:
                print(f'Bibox auth order detail error: {resp["result"][0]["error"]}')
            return order_detail
        except Exception as e:
            print(f'Bibox auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/v1/transfer'
            params = {'select': 1}
            params = self._sign_message('transfer/assets', params)

            resp = requests.post(url, data=params)
            balance, frozen = {}, {}
            resp = resp.json()
            if 'result' in resp.keys():
                wallet = resp['result'][0]['result']['assets_list']
                balance = {row['coin_symbol']: float(row['balance']) for row in wallet}
                frozen = {row['coin_symbol']: float(row['freeze']) for row in wallet}
            else:
                print(f'Bibox auth wallet balance error: {resp.json()["error"]}')
            return balance, frozen
        except Exception as e:
            print(f'Bibox auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = BiboxAuth('https://api.bibox.com', '59ed9c456d6d1d5bc843ac2fde9fdbe34b820a89', '851fdebdc8a40d20b70056d08e0dd3a2cbacc35d')
    # print(bit.place_order('BTC_USDT', 1.0016, 1.5, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.wallet_balance())
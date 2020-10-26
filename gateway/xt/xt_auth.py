import requests
import hashlib
import time
import hmac
import json


class XtAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _symbol_convert(self, symbol: str):
        return symbol.lower()

    def _timestamp(self):
        return round(time.time()*1000)

    def _sign_message(self, params):
        try:
            paramStr = []
            if params is not None:
                for key in sorted(params.keys()):
                    paramStr.append(f'{key}={params[key]}')
            paramStr = '&'.join(paramStr)
            sign = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(paramStr, encoding='utf-8'), hashlib.sha256).hexdigest()
            return sign
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/trade/api/v1/order'
            params = {
                'accesskey': self.api_key,
                'market': self._symbol_convert(symbol),
                'type': 1 if side == 'buy' else 0,
                'entrustType': 0,
                'price': price,
                'number': amount,
                'nonce': self._timestamp(),
            }
            params['signature'] = self._sign_message(params)
            resp = requests.post(url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            if resp['code'] == 200:
                return resp['data']['id']
            else:
                print(f'Xt auth place order error: {resp}')
                return None
        except Exception as e:
            print(f'Xt auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/trade/api/v1/cancel'
            params = {
                'accesskey': self.api_key,
                'market': self._symbol_convert(symbol),
                'id': order_id,
                'nonce': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            resp = requests.post(url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            data = False
            if resp['code'] == 200:
                data = True
                message = resp['info']
            else:
                message = resp
                print(f'Xt auth cancel order error: {message}')
            info = {
                "func_name": "cancel_order",
                "order_id": order_id,
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Xt auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_order',
                    'message': 'orders are empty',
                    'data': False
                }
            orders_id = []
            for order in orders:
                if order['side'] == side:
                    orders_id.append(order['order_id'])
            url = self.urlbase + '/trade/api/v1/batchCancel'
            params = {
                'accesskey': self.api_key,
                'nonce': self._timestamp(),
                'market': self._symbol_convert(symbol),
                'data': json.dumps(orders_id),
            }
            params['signature'] = self._sign_message(params)

            resp = requests.delete(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            data = False
            if resp['code'] == 200:
                data = True
                message = resp
            else:
                message = resp
                print(f'Xt auth cancel order error: {message}')
            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Xt auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        try:
            url = self.urlbase + '/trade/api/v1/getOpenOrders'
            params = {
                'accesskey': self.api_key,
                'nonce': self._timestamp(),
                'market': self._symbol_convert(symbol),
                'page': offset,
                'pageSize': limit
            }
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            results = []
            if resp['code'] == 200:
                for order in resp['data']:
                    results.append({
                        'order_id': order['id'],
                        'symbol': symbol,
                        'original_amount': float(order['number']),
                        'price': float(order['price']),
                        'side': 'buy' if order['type'] == 1 else 'sell',
                        'price_avg': float(order['avgPrice']),
                        'filled_amount': float(order['completeNumber']),
                        'create_time': round(order['time'] / 1000),
                    })
            else:
                print(f'Xt auth open order error: {resp}')
            return results
        except Exception as e:
            print(f'Xt auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/trade/api/v1/getOrder'
            params = {
                'accesskey': self.api_key,
                'nonce': self._timestamp(),
                'market': self._symbol_convert(symbol),
                'id': order_id
            }
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            result = {}
            if resp['code'] == 200:
                message = 'OK'
                order = resp['data']
                result = {
                    'order_id': order['id'],
                    'symbol': symbol,
                    'original_amount': float(order['number']),
                    'price': float(order['price']),
                    'side': 'buy' if order['type'] == 1 else 'sell',
                    'price_avg': float(order['avgPrice']),
                    'filled_amount': float(order['completeNumber']),
                    'create_time': round(order['time'] / 1000),
                }
            else:
                message = resp['info']
                print(f'Xt auth order detail error: {message}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': message,
                'data': result
            }
            return info
        except Exception as e:
            print(f'Xt auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/trade/api/v1/getBalance'
            params = dict()
            params['accesskey'] = self.api_key
            params['nonce'] = self._timestamp()
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
            balance, frozen = {}, {}
            if resp['code'] == 200:
                wallet = resp['data']
                balance = {row: float(wallet[row]['available']) for row in wallet.keys()}
                frozen = {row: float(wallet[row]['freeze']) for row in wallet.keys()}
            else:
                print(f'Xt auth error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Xt auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    binance = XtAuth('https://api.xt.com', '09e570e3-bb4b-4fe0-933e-d4af2163a0a3',
                          '64c02d104b2e1c5f19eb9e4bb1cdf398b518bfdd')
    # print(binance.place_order("BTC_USDT", 30, 0.01, "buy"))
    # print(binance.order_detail('BTC_USDT', '1'))
    # print(binance.open_orders('BTC_USDT'))
    # print(binance.cancel_order('BTC_USDT', '1'))
    # print(binance.cancel_all('BTC_USDT', 'sell'))
    # print(binance.wallet_balance())
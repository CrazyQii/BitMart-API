"""
binance鉴权接口
2020/10/10 hlq
"""

from binance.binance_public import BinancePublic
import hmac
import hashlib
import time


class BinanceAuth(BinancePublic):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase

    def _sign_message(self, param: dict):
        """ authtication """
        try:
            query_string = ''
            if param is not None:
                query_string = '&'.join([str(key) + '=' + str(value) for (key, value) in param.items()])
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(query_string, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def _timestamp(self):
        return round(time.time()*1000)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'side': side,
                'type': 'limit',
                'price': price,
                'quantity': amount,
                'timestamp': self._timestamp(),
                'timeInForce': 'GTC'
            }
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('POST', url, data=params, headers={'X-MBX-APIKEY': self.api_key})
            if is_ok:
                return content
            else:
                self._output('place_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, symbol: str, entrust_id: str):
        try:
            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'orderId': entrust_id,
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('DELETE', url, data=params, headers={'X-MBX-APIKEY': self.api_key})
            if is_ok:
                info = {
                    "func_name": 'cancel_order',
                    "entrust_id": entrust_id,
                    "response": content
                }
                print(info)
                return is_ok
            else:
                self._output('cancel_order', content)
        except Exception as e:
            print(e)

    def open_orders(self, symbol: str):
        try:
            url = self.urlbase + '/api/v3/allOrders'
            params = {
                'symbol': self._symbol_convert(symbol),
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('GET', url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            if is_ok:
                results = []
                for order in content:
                    results.append({
                        'entrust_id': order['orderId'],
                        'side': order['side'],
                        'symbol': order['symbol'],
                        'status': order['status'],
                        'timestamp': order['time'],
                        'price': order['price'],
                        'original_amount': order['origQty'],
                        'executed_amount': order['executedQty'],
                        'remaining_amount': float(order['origQty']) - float(order['executedQty']),
                        'fees': None
                    })
                return results
            else:
                return self._output('open_orders', content)
        except Exception as e:
            print(e)

    def order_detail(self, symbol: str, entrust_id: str):
        try:
            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'orderId': entrust_id,
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('GET', url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            if is_ok:
                content = content['data']
                return {
                    'entrust_id': content['orderId'],
                    'side': content['side'],
                    'symbol': content['symbol'],
                    'status': content['status'],
                    'timestamp': content['time'],
                    'price': content['price'],
                    'original_amount': content['origQty'],
                    'executed_amount': content['executedQty'],
                    'remaining_amount': float(content['origQty']) - float(content['executedQty']),
                    'fees': None
                }
            else:
                self._output('order_detail', content)
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            url = self.urlbase + '/api/v3/account'
            params = dict()
            params['timestamp'] = self._timestamp()
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('GET', url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            if is_ok:
                free, frozen = {}, {}
                for currency in content['balances']:
                    free[currency['asset']], frozen[currency['asset']] = currency['free'], currency['locked']
                return free, frozen
            else:
                self._output('wallet_balance', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    binance = BinanceAuth('https://api.binance.com', 'peHvRKu7QGVZIezAlZfIAhmK5zPxa5ptLo6kkMOLGeJpD1UJhpufUVY6WvYqrDrh', 'GS6Us3YWMw7sQQMEm5uC90CrgFcvtSOlGyz3PzWA5KXsUamYG4Y4ieqW6oziKZ72')
    # print(binance.place_order('BTC_USDT', 1, 0.1, 'buy'))
    # print(binance.order_detail('BTC_USDT', '1'))
    # print(binance.open_orders('BTC_USDT'))
    # print(binance.cancel_order('UMA_USDT', '1'))
    # print(binance.wallet_balance())

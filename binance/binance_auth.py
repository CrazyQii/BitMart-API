# -*- coding: utf-8 -*-
"""
binance spot authentication API
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
        """
        Place order
        """
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
                return content['orderId']
            else:
                self._output('place_order', content)
                return None
        except Exception as e:
            print(e)
            return None

    def cancel_order(self, symbol: str, entrust_id: str):
        """
        cancel order
        """
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
                return None
        except Exception as e:
            print(e)
            return None

    def open_orders(self, symbol: str):
        """
        Get a list of user orders
        """
        try:
            url = self.urlbase + '/api/v3/allOrders'
            params = {
                'symbol': self._symbol_convert(symbol),
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('GET', url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            results = []
            if is_ok:
                for order in content:
                    results.append({
                        'entrust_id': order['orderId'],
                        'side': order['side'],
                        'symbol': order['symbol'],
                        'status': order['status'],
                        'timestamp': round(order['time'] / 1000),
                        'price': float(order['price']),
                        'original_amount': float(order['origQty']),
                        'executed_amount': float(order['executedQty']),
                        'remaining_amount': float(order['origQty']) - float(order['executedQty']),
                        'fees': None
                    })
            else:
                self._output('open_orders', content)
            return results
        except Exception as e:
            print(e)
            return None

    def order_detail(self, symbol: str, entrust_id: str):
        """
        Get order detail
        """
        try:
            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'orderId': entrust_id,
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('GET', url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            result = {}
            if is_ok:
                content = content['data']
                result = {
                    'entrust_id': content['orderId'],
                    'side': content['side'],
                    'symbol': content['symbol'],
                    'status': content['status'],
                    'timestamp': round(content['time'] / 1000),
                    'price': float(content['price']),
                    'original_amount': float(content['origQty']),
                    'executed_amount': float(content['executedQty']),
                    'remaining_amount': float(content['origQty']) - float(content['executedQty']),
                    'fees': None
                }
            else:
                self._output('order_detail', content)
            return result
        except Exception as e:
            print(e)
            return None

    def wallet_balance(self):
        """
        Get the user's wallet balance for all currencies
        """
        try:
            url = self.urlbase + '/api/v3/account'
            params = dict()
            params['timestamp'] = self._timestamp()
            params['signature'] = self._sign_message(params)

            is_ok, content = self._request('GET', url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            free, frozen = {}, {}
            if is_ok:
                for currency in content['balances']:
                    free[currency['asset']], frozen[currency['asset']] = currency['free'], currency['locked']
            else:
                self._output('wallet_balance', content)
            return free, frozen
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    binance = BinanceAuth('https://api.binance.com', 'peHvRKu7QGVZIezAlZfIAhmK5zPxa5ptLo6kkMOLGeJpD1UJhpufUVY6WvYqrDrh', 'GS6Us3YWMw7sQQMEm5uC90CrgFcvtSOlGyz3PzWA5KXsUamYG4Y4ieqW6oziKZ72')
    # print(binance.place_order("XRP_BTC", 30, 0.0002, "sell"))
    # print(binance.order_detail('BTC_USDT', '1'))
    # print(binance.open_orders('BTC_USDT'))
    # print(binance.cancel_order('UMA_USDT', '1'))
    # print(binance.wallet_balance())

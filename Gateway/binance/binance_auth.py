# -*- coding: utf-8 -*-
import hmac
import hashlib
import time
import requests


class BinanceAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_'))

    def _sign_message(self, param: dict):
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

    def _price_filter(self, symbol: str):
        max_price = 0.0
        min_price = 0.0
        try:
            url = self.urlbase + '/api/v3/exchangeInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()['symbols']
                for symbols in resp:
                    if self._symbol_convert(symbol) == symbols['symbol']:
                        max_price = float(symbols['filters'][0]['maxPrice'])
                        min_price = float(symbols['filters'][0]['minPrice'])
            else:
                print(f'price filter error {resp.json()["msg"]}')
            return {'min_price': min_price, 'max_price': max_price}
        except Exception as e:
            print(f'price filter error {e}')
            return {'min_price': min_price, 'max_price': max_price}

    def _quantity_filter(self, symbol: str):
        max_Qty = 0.0
        min_Qty = 0.0
        try:
            url = self.urlbase + '/api/v3/exchangeInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()['symbols']
                for symbols in resp:
                    if self._symbol_convert(symbol) == symbols['symbol']:
                        max_Qty = float(symbols['filters'][2]['maxQty'])
                        min_Qty = float(symbols['filters'][2]['minQty'])
            else:
                print(f'price filter error {resp.json()["msg"]}')
            return {'min_Qty': min_Qty, 'max_Qty': max_Qty}
        except Exception as e:
            print(f'price filter error {e}')
            return {'min_Qty': min_Qty, 'max_Qty': max_Qty}

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            # price filter
            min_price = self._price_filter(symbol)['min_price']
            max_price = self._price_filter(symbol)['max_price']
            if price > max_price or price < min_price:
                print(f'price must in [{min_price}, {max_price}]')
                return None

            min_Qty = self._quantity_filter(symbol)['min_Qty']
            max_Qty = self._quantity_filter(symbol)['max_Qty']
            if amount > max_Qty or amount < min_Qty:
                print(f'quantity must in [{min_Qty}, {max_Qty}]')
                return None

            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'side': side,
                'type': 'LIMIT',
                'price': price,
                'quantity': amount,
                'timestamp': self._timestamp(),
                'timeInForce': 'GTC'
            }
            params['signature'] = self._sign_message(params)

            resp = requests.post(url, data=params, headers={'X-MBX-APIKEY': self.api_key})
            if resp.status_code == 200:
                resp = resp.json()
                return resp['orderId']
            else:
                print(f'Binance auth place order error: {resp.json()["msg"]}')
        except Exception as e:
            print(f'Binance auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'orderId': order_id,
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            resp = requests.delete(url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            data = False
            if resp.status_code == 200:
                data = True
                message = 'OK'
            else:
                message = resp.json()['msg']
                print(f'Binance auth error: {message}')
            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Binance auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_all',
                    'message': 'Empty orders',
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
            print(f'Binance auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:
            orders = self.order_list(symbol, limit=500)
            return orders
        except Exception as e:
            print(f'Binance auth open orders error: {e}')

    def order_list(self, symbol: str, status: list = None, offset=1, limit=100):
        if status is None:
            status = ['NEW', 'PARTIALLY_FILLED']
        try:
            url = self.urlbase + '/api/v3/openOrders'
            params = {
                'symbol': self._symbol_convert(symbol),
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            results = []
            if resp.status_code == 200:
                resp = resp.json()
                i = 0
                for order in resp:
                    if i > limit:
                        break
                    if order['status'] in status:
                        results.append({
                            'order_id': order['orderId'],
                            'symbol': symbol,
                            'original_amount': float(order['origQty']),
                            'price': float(order['price']),
                            'side': order['side'],
                            'price_avg': float(order['cummulativeQuoteQty']) / float(order['executedQty']) if float(order['executedQty']) > 0 else 0,
                            'filled_amount': float(order['executedQty']),
                            'create_time': round(order['time'] / 1000),
                        })
                    i = i + 1
            else:
                print(f'Binance auth open order error: {resp.json()["msg"]}')
            return results
        except Exception as e:
            print(f'Binance auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/api/v3/order'
            params = {
                'symbol': self._symbol_convert(symbol),
                'orderId': order_id,
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            result = {}
            if resp.status_code == 200:
                order = resp.json()
                result = {
                    'order_id': order['orderId'],
                    'symbol': symbol,
                    'price': float(order['price']),
                    'amount': float(order['origQty']),
                    'side': order['side'],
                    'price_avg': None,
                    'filled_amount': float(order['executedQty']),
                    'status': order['status'],
                    'create_time': round(order['time'] / 1000),
                }
                message = 'OK'
            else:
                message = resp.json()["msg"]
                print(f'Binance auth order detail error: {message}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': message,
                'data': result
            }
            return info
        except Exception as e:
            print(f'Binance auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/api/v3/myTrades'
            params = {
                'symbol': self._symbol_convert(symbol),
                'limit': limit,
                'timestamp': self._timestamp()
            }
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'detail_id': trade['id'],
                        'order_id': trade['orderId'],
                        'symbol': symbol,
                        'create_time': round(trade['time'] / 1000),
                        'side': 'buy' if trade['isBuyer'] else 'sell',
                        'price_avg': None,
                        'notional': float(trade['price']),
                        'size': float(trade['qty']),
                        'fees': float(trade['commission']),
                        'fee_coin_name': trade['commissionAsset'],
                        'exec_type': 'M' if trade['isMaker'] else 'T',
                    })
            else:
                print(f'Binance auth user trades error: {resp.json()["msg"]}')
            return trades
        except Exception as e:
            print(f'Binance auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/api/v3/account'
            params = dict()
            params['timestamp'] = self._timestamp()
            params['signature'] = self._sign_message(params)

            resp = requests.get(url, params=params, headers={'X-MBX-APIKEY': self.api_key})
            balance, frozen = {}, {}
            if resp.status_code == 200:
                wallet = resp.json()['balances']
                balance = {row['asset']: float(row['free']) for row in wallet}
                frozen = {row['asset']: float(row['locked']) for row in wallet}
            else:
                print(f'Binance auth wallet balance error: {resp.json()["msg"]}')
            return balance, frozen
        except Exception as e:
            print(f'Binance auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    binance = BinanceAuth('https://api.binance.com', 'peHvRKu7QGVZIezAlZfIAhmK5zPxa5ptLo6kkMOLGeJpD1UJhpufUVY6WvYqrDrh', 'GS6Us3YWMw7sQQMEm5uC90CrgFcvtSOlGyz3PzWA5KXsUamYG4Y4ieqW6oziKZ72')
    print(binance.place_order('BTC_USDT', 30, 0.01, 'buy'))
    print(binance.order_detail('BTC_USDT', '1'))
    print(binance.open_orders('BTC_USDT'))
    print(binance.cancel_order('BTC_USDT', '1'))
    print(binance.cancel_all('BTC_USDT', 'sell'))
    print(binance.user_trades('BTC_USDT'))
    print(binance.wallet_balance())

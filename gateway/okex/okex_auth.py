# -*- coding: utf-8 -*-
"""
okex spot authentication API
2020/10/14 hlq
"""
from datetime import datetime
from urllib.parse import urlencode
import base64
import hmac
import json
import requests


class OkexAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
    
    def _symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _get_utc(self):
        return datetime.utcnow().isoformat('T', 'milliseconds') + 'Z'

    def _sign_message(self, message):
        try:
            mac = hmac.new(bytes(self.api_secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            return base64.b64encode(d)
        except Exception as e:
            print(e)

    def _request(self, method, path, params):
        try:
            url = self.urlbase + path
            ts = self._get_utc()
            if method == 'POST':
                msg = f'{ts}{method}{path}{json.dumps(params)}'
                signature = self._sign_message(msg)
                headers = {
                    'OK-ACCESS-KEY': self.api_key,
                    'OK-ACCESS-SIGN': signature,
                    'OK-ACCESS-TIMESTAMP': ts,
                    'OK-ACCESS-PASSPHRASE': self.passphrase,
                    'Content-Type': 'application/json'
                }
                resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            else:
                if len(params) == 0:
                    msg = f'{ts}{method}{path}'
                else:
                    msg = f'{ts}{method}{path}?{urlencode(params)}'
                signature = self._sign_message(msg)
                headers = {
                    'OK-ACCESS-KEY': self.api_key,
                    'OK-ACCESS-SIGN': signature,
                    'OK-ACCESS-TIMESTAMP': ts,
                    'OK-ACCESS-PASSPHRASE': self.passphrase,
                    'Content-Type': 'application/json'
                }
                resp = requests.get(url, params=params, headers=headers).json()
            return resp
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            params = {
                'type': 'limit',
                'side': side,
                'instrument_id': self._symbol_convert(symbol),
                'size': amount,
                'price': price
            }
            resp = self._request('POST', '/api/spot/v3/orders', params)
            if resp['result']:
                return resp['order_id']
            else:
                print(f'Okex auth error: {resp["error_message"]}')
                return None
        except Exception as e:
            print(f'Okex auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            params = {
                "instrument_id": self._symbol_convert(symbol)
            }
            resp = self._request('POST', f'/api/spot/v3/cancel_orders/{order_id}', params)
            data = False
            if resp['result']:
                data = True
                message = resp['error_message']
            else:
                message = resp['error_message']
                print(f'Okex auth cancel order error: {message}')
            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Okex auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                info = {
                    'func_name': 'cancel_all',
                    'message': 'Empty order',
                    'data': False
                }
                return info

            order_ids = []
            for order in orders:
                if order['side'] == side:
                    order_ids.append(order['order_id'])
            params = {
                'instrument_id': self._symbol_convert(symbol),
                'order_ids': order_ids
            }
            resp = self._request('POST', '/api/spot/v3/cancel_batch_orders', params)
            data = False
            if resp['result']:
                data = True
                message = resp['error_message']
            else:
                message = resp['error_message']
                print(f'Okex auth cancel all error: {message}')

            info = {
                'func_name': 'cancel_all',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Okex auth cancel all error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            params = {
                'instrument_id': self._symbol_convert(symbol)
            }
            resp = self._request('GET', f'/api/spot/v3/orders/{order_id}', params)
            order_detail = {}
            if 'code' not in resp:
                order_detail = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'side': resp['side'],
                    'price': float(resp['price']),
                    'amount': float(resp['size']),
                    'price_avg': float(resp['price_avg']),
                    'filled_amount': float(resp['filled_size']),
                    'status': resp['state'],
                    'timestamp': self._utc_to_ts(resp['timestamp'])
                }
                message = 'ok'
            else:
                message = resp['error_message']
                print(f'Okex auth order detail error: {message}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': message,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Okex auth order detail error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                if len(orders) == 0:
                    orders_on_this_page = self.order_list(symbol, status=6)
                else:
                    last_id = orders[-1]['order_id']
                    orders_on_this_page = self.order_list(symbol, status=6, before=last_id)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
                else:
                    break
            return orders
        except Exception as e:
            print(f'Okex auth open orders error: {e}')

    def order_list(self, symbol: str, status=6, before=None, limit=100):
        try:
            params = {
                'instrument_id': self._symbol_convert(symbol),
                'state': status,
                'limit': limit
            }
            if before is not None:
                params.update({'before': before})
            resp = self._request('GET', '/api/spot/v3/orders', params)
            results = []
            if 'code' not in resp:
                for order in resp:
                    results.append({
                        'order_id': order['order_id'],
                        'symbol': symbol,
                        'side': order['side'],
                        'price': float(order['price']),
                        'amount': float(order['size']),
                        'price_avg': float(order['price_avg']),
                        'filled_amount': float(order['filled_size']),
                        'timestamp': self._utc_to_ts(order['timestamp'])
                    })
            else:
                print(f'Okex auth open order error: {resp["error_message"]}')
            return results
        except Exception as e:
            print(f'Okex auth open order error: {e}')

    def wallet_balance(self):
        try:
            resp = self._request('GET', '/api/spot/v3/accounts', {})
            balance, frozen = {}, {}
            if 'code' not in resp:
                wallet = resp
                balance = {row["currency"]: float(row["available"]) for row in wallet}
                frozen = {row["currency"]: float(row["hold"]) for row in wallet}
            else:
                print(f'Okex auth wallet balance error: {resp["err_message"]}')
            return balance, frozen
        except Exception as e:
            print(f'Okex auth wallet balance error: {e}')
            return {}, {}


if __name__ == "__main__":
    okex = OkexAuth("https://www.okex.com", "dda0063c-70fc-42b1-8390-281e77b532a5", "A06AFB73716F15DC1805D183BCE07BED", "okexpassphrase")
    # print(okex.place_order("XRP_BTC", 30, 0.0002, "sell"))
    # print(okex.cancel_order("XRP_BTC", '123'))
    # print(okex.order_detail("XRP_BTC", '123'))
    # print(okex.cancel_all('XRP_BTC', 'sell'))
    # print(okex.open_orders("XRP_BTC"))
    # print(okex.wallet_balance())

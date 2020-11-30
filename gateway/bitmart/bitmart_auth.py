# -*- coding: utf-8 -*-
"""
bitmart spot authentication API
2020/10/10 hlq
"""

import hmac
import hashlib
import time
import json
import requests


class BitmartAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _timestamp(self):
        return str(round(time.time()*1000))

    def _sign_message(self, timestamp, params):
        """ authtication """
        try:
            # signature string
            sign_str = f'{timestamp}#{self.memo}#{json.dumps(params)}'
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(sign_str, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(f'Bitmart auth: sign message error: {e}')

    def _request(self, url, get_post, params):
        """request"""
        try:
            timestamp = self._timestamp()
            if get_post == "POST":
                headers = {
                    'Content-type': 'application/json',
                    'X-BM-KEY': self.api_key,
                    'X-BM-SIGN': self._sign_message(timestamp, params),
                    'X-BM-TIMESTAMP': timestamp
                }
                resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            else:
                headers = {
                    'Content-type': 'application/json',
                    'X-BM-KEY': self.api_key,
                    'X-BM-TIMESTAMP': self._timestamp()
                }
                resp = requests.get(url, headers=headers).json()
            return resp
        except Exception as e:
            print(f'Bitmart auth: request error: {e}')

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        if side not in ['buy', 'sell']:
            print('side is wrong')
            return None
        try:
            url = self.urlbase + '/spot/v1/submit_order'

            params = {
                'symbol': symbol,
                'side': side,
                'type': 'limit',
                'size': amount,
                'price': price
            }
            resp = self._request(url, 'POST', params)
            if resp['code'] == 1000:
                return resp['data']['order_id']
            else:
                print(f'Bitmart auth: error: {resp["message"]}')
                return None
        except Exception as e:
            print(f'Bitmart auth: place order error: {e}')

    def place_oc_order(self, symbol, amount, price, side):
        try:
            #code: 1000; 50020（余额不足）; 50019（高于盘口）; 50008(低于盘口)
            url = self.urlbase + '/spot/custom'

            params = {
                'symbol': symbol,
                'taker': side,
                'size': amount,
                'price': price
            }
            resp = self._request(url, 'POST', params)
            if resp["code"] == 1000:
                content = resp["data"]
            else:
                content = resp["message"]
                print("place oc order %s" % content)
            return resp["code"]
        except Exception as e:
            print("Bitmart auth: place oc order error: %s" % e)

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/spot/v2/cancel_order'
            params = {
                'symbol': symbol,
                'order_id': order_id,
            }
            resp = self._request(url, 'POST', params)
            data = False
            if resp['code'] == 1000:
                data = resp['data']
                message = resp['message']
            else:
                message = resp['message']
                print(f'Bitmart auth error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Bitmart auth: cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            url = self.urlbase + f'/spot/v1/cancel_orders'

            params = {
                'symbol': symbol,
                'side': side,
            }
            resp = self._request(url, 'POST', params)
            data = False
            if resp['code'] == 1000:
                data = resp['data']
                message = resp['message']
            else:
                message = resp['message']
                print(f'Bitmart auth error: {message}')

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Bitmart auth cancel order error: {e}')

    def open_orders(self, symbol):
        try:    
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, 9, page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print("Bitmart auth open orders error: %s" % e)

    def order_list(self, symbol: str, status=9, offset=1, limit=100):
        try:
            url = self.urlbase + f'/spot/v1/orders?symbol={symbol}&status={status}&offset={offset}&limit={limit}'
            
            params = {}
            resp = self._request(url, 'GET', params)
            results = []
            if resp['code'] == 1000:
                for order in resp['data']['orders']:
                    results.append({
                        'order_id': order['order_id'],
                        'symbol': order['symbol'],
                        'amount': float(order['size']),
                        'price': float(order['price']),
                        'side': order['side'],
                        'price_avg': float(order['price_avg']),
                        'filled_amount': float(order['filled_size']),
                        'create_time': int(order['create_time']/1000)
                    })
            else:
                print(f'Bitmart auth error: {resp["message"]}')
            return results
        except Exception as e:
            print(f'Bitmart auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + f'/spot/v1/order_detail?symbol={symbol}&order_id={order_id}'

            params = {}
            resp = self._request(url, 'GET', params)
            order_detail = {}
            if resp['code'] == 1000:
                content = resp['data']
                order_detail = {
                    'order_id': content['order_id'],
                    'symbol': content['symbol'],
                    'side': content['side'],
                    'price': float(content['price']),
                    'amount': float(content['size']),
                    'price_avg': float(content['price_avg']),
                    'filled_amount': float(content['filled_size']),
                    'status': float(content['status']),
                    'create_time': content['create_time']/1000
                }
            else:
                print(f'Bitmart auth error: {resp["message"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp['message'],
                'data': order_detail
            }
            return info 
        except Exception as e:
            print(f'Bitmart auth order detail error: {e}')

    def user_trades(self, symbol, offset=1, limit=100):
        try:
            url = self.urlbase + f'/spot/v1/trades?symbol={symbol}&limit={limit}&offset={offset}'
            
            params = {}
            resp = self._request(url, 'GET', params)
            user_trades = []

            if resp["code"] == 1000:
                content = resp["data"]["trades"]
                for trade in content:
                    user_trades.append({
                        'detail_id': trade['detail_id'],
                        'order_id': trade['order_id'],
                        'symbol': trade['symbol'],
                        'create_time': int(trade['create_time']/1000),
                        'side': trade['side'],
                        'fees': float(trade['fees']),
                        'fee_coin_name': trade['fee_coin_name'],
                        'notional': float(trade['notional']),
                        'price_avg': float(trade['price_avg']),
                        'amount': float(trade['size']),
                        'exec_type': trade['exec_type']
                    })
            else:
                message = resp["message"]
                print("Bitmart auth error: %s" % message)
            return user_trades
        except Exception as e:
            print("Bitmart auth get user trades error: %s" % e)

    def wallet_balance(self):
        try:
            url = self.urlbase + '/spot/v1/wallet'
            
            params = {}
            resp = self._request(url, 'GET', params)
            balance, frozen = {}, {}
            if resp['code'] == 1000:
                wallet = resp["data"]["wallet"]
                balance = {row["id"]: float(row["available"]) for row in wallet}
                frozen = {row["id"]: float(row["frozen"]) for row in wallet}
            else:
                print(f'Bitmart auth error: {resp["message"]}')
            return balance, frozen
        except Exception as e:
            print(f'Bitmart auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = BitmartAuth('https://api-cloud.bitmart.news', '5de397b9cef8bebc31f65e124c3a4a162d6d1f99', 'f4b7c83dc9c6790d6ea344ba3beafdfd70fe9481dccc7e70f0dd7d84b76e1ed2', 'mock')
    print(bit.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.wallet_balance())
    # print(bit.user_trades("BTC_USDT"))

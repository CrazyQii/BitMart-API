"""
bitmart鉴权接口
2020/10/10 hlq
"""

from bitmart.bitmart_public import BitmartPublic
import hmac
import hashlib
import time
import json


class BitmartAuth(BitmartPublic):
    def __init__(self, urlbase, api_key, api_secret, memo):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = memo

    def _sign_message(self, query_string):
        """ authtication """
        try:
            # signature string
            sign_str = f'{self._timestamp()}#{self.memo}#{query_string}'
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(sign_str, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def _timestamp(self):
        return str(round(time.time()*1000))

    def place_order(self, symbol: str, amount: float, price: float, side: str, type='limit'):
        try:
            url = self.urlbase + '/spot/v1/submit_order'
            params = {
                'symbol': symbol,
                'side': side,
                'type': type,
                'price': price,
                'size': amount
            }
            print(self._sign_message(json.dumps(params)))
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-SIGN': self._sign_message(json.dumps(params)),
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            is_ok, content = self._request('POST', url, data=json.dumps(params), headers=headers)
            if is_ok:
                return content
            else:
                self._output('place_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, symbol: str, entrust_id: str):
        try:
            url = self.urlbase + '/spot/v2/cancel_order'
            params = {
                'symbol': symbol,
                'order_id': entrust_id,
            }
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-SIGN': self._sign_message(json.dumps(params)),
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            is_ok, content = self._request('POST', url, data=json.dumps(params), headers=headers)
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

    def open_orders(self, symbol: str, status=1, offset=1, limit=100):
        try:
            url = self.urlbase + f'/spot/v1/orders?symbol={symbol}&status={status}&offset={offset}&limit={limit}'
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            is_ok, content = self._request('GET', url, headers=headers)
            if is_ok:
                results = []
                for order in content['data']['orders']:
                    results.append({
                        'entrust_id': order['order_id'],
                        'side': order['side'],
                        'symbol': order['symbol'],
                        'status': order['status'],
                        'timestamp': order['create_time'],
                        'price': order['price'],
                        'original_amount': order['size'],
                        'executed_amount': order['filled_size'],
                        'remaining_amount': float(order['size']) - float(order['filled_size']),
                        'fees': None
                    })
                return results
            else:
                return self._output('open_orders', content)
        except Exception as e:
            print(e)

    def order_detail(self, symbol: str, entrust_id: str):
        try:
            url = self.urlbase + '/spot/v1/order_detail'
            params = {'symbol': symbol, 'order_id': entrust_id}
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }

            is_ok, content = self._request('GET', url, params=params, headers=headers)
            if is_ok:
                content = content['data']
                return {
                    'entrust_id': content['order_id'],
                    'side': content['side'],
                    'symbol': content['symbol'],
                    'status': content['status'],
                    'timestamp': content['create_time'],
                    'price': content['price'],
                    'original_amount': content['size'],
                    'executed_amount': content['filled_size'],
                    'remaining_amount': float(content['size']) - float(content['filled_size']),
                    'fees': None
                }
            else:
                self._output('order_detail', content)
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            url = self.urlbase + '/spot/v1/wallet'
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }
            is_ok, content = self._request('GET', url, headers=headers)
            if is_ok:
                free, frozen = {}, {}
                for currency in content['data']['wallet']:
                    free[currency['id']], frozen[currency['id']] = currency['available'], currency['frozen']
                return free, frozen
            else:
                self._output('wallet_balance', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    bit = BitmartAuth('https://api-cloud.bitmart.info', '5de397b9cef8bebc31f65e124c3a4a162d6d1f99', 'f4b7c83dc9c6790d6ea344ba3beafdfd70fe9481dccc7e70f0dd7d84b76e1ed2', 'mock')
    # print(bit.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    # print(bit.wallet_balance())

"""
hoo鉴权接口
2020-9-30 hlq
"""

from faker import Faker
from hoo.hoo_public import HooPublic
import hmac
import hashlib
import time
import json

f = Faker(locale='zh-CN')


class HooAuth(HooPublic):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase

    def _sign_message(self):
        """ authtication """
        try:
            # signature string
            nonce = f.md5()
            ts = int(time.time())
            sign_str = f'client_id={self.api_key}&nonce={nonce}&ts={ts}'
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(sign_str, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            sign = {
                'nonce': nonce,
                'ts': ts,
                'client_id': self.api_key,
                'sign': digest
            }
            return sign
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/open/v1/orders/place'
            params = self._sign_message()
            params.update({
                'symbol': self._symbol_convert(symbol),
                'quantity': amount,
                'price': price,
                'side': 1 if side == 'buy' else -1
            })
            is_ok, content = self._request('POST', url, data=params)
            if is_ok:
                if content['code'] == 0:
                    return content['data']
                else:
                    return content
            else:
                self._output('place_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, symbol: str, entrust_id: str, trade_no: str):
        # must contain entrust_id and trade_no
        try:
            url = self.urlbase + '/open/v1/orders/cancel'
            params = self._sign_message()
            params.update({
                'symbol': self._symbol_convert(symbol),
                'order_id': entrust_id,
                'trade_no': trade_no
            })
            is_ok, content = self._request('POST', url, data=json.dumps(params))
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

    def open_orders(self, symbol: str, pagenum: int = None, pagesize: int = None, side: int = None, start: int = None,
               end: int = None):
        try:
            url = self.urlbase + '/open/v1/orders'
            params = self._sign_message()
            params.update({'symbol': self._symbol_convert(symbol)})

            is_ok, content = self._request('GET', url, params=params)
            if is_ok:
                results = []
                for order in content['data']['orders']:
                    results.append({
                        'status': order['status'],
                        'remaining_amount': float(order['quantity']) - float(order['match_qty']),
                        'timestamp': order['create_at'],
                        'price': order['price'],
                        'executed_amount': order['match_qty'],
                        'symbol': order['ticker'],
                        'fees': order['fee'],
                        'original_amount': order['quantity'],
                        'entrust_id': order['order_id'],
                        'side': 'buy' if order['side'] == 1 else 'sell'
                    })
                return results
            else:
                return self._output('open_orders', content)
        except Exception as e:
            print(e)

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/open/v1/orders/detail'
            params = self._sign_message()
            params.update({'symbol': self._symbol_convert(symbol), 'order_id': order_id})

            is_ok, content = self._request('GET', url, params=params)
            if is_ok:
                if content['code'] == 0:
                    return {
                        'status': content['status'],
                        'remaining_amount': float(content['quantity']) - float(content['match_qty']),
                        'timestamp': content['create_at'],
                        'price': content['price'],
                        'executed_amount': content['match_qty'],
                        'symbol': content['ticker'],
                        'fees': content['fee'],
                        'original_amount': content['quantity'],
                        'entrust_id': content['order_id'],
                        'side': 'buy' if content['side'] == 1 else 'sell'
                    }
                else:
                    return content
            else:
                self._output('order_detail', content)
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            url = self.urlbase + '/open/v1/balance'
            params = self._sign_message()
            is_ok, content = self._request('GET', url, params=params)
            if is_ok:
                free, frozen = {}, {}
                if content['code'] == 0:
                    for currency in content['data']:
                        free[currency['symbol']], frozen[currency['symbol']] = currency['amount'], currency['freeze']
                return free, frozen
            else:
                self._output('wallet_balance', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    hoo = HooAuth('https://api.hoolgd.com', 'iJsVEJDESyTXdm8hRBuf79fANdwNB5', 'J7EqDCc6FaKA8n5nCy8WJ1uoM4HSZeg2k43mepX5TNjz1qLHUs')
    # print(hoo.place_order('EOS_USDT', 1.0016, 11, 'sell'))
    # print(hoo.order_detail('BTC_USDT', '1'))
    # print(hoo.open_orders('BTC_USDT'))
    # print(hoo.cancel_order('UMA_USDT', '1', '2'))
    # print(hoo.wallet_balance())

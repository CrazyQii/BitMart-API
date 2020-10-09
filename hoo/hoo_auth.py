"""
鉴权接口
2020-9-30 hlq
"""

from faker import Faker
from hoo.hoo_public import HooPublic
import hmac
import hashlib
import time

f = Faker(locale='zh-CN')


class HooAuth(HooPublic):
    def __init__(self, urlbase, api_key, api_secret):
        super().__init__(urlbase)
        self.api_key = api_key
        self.client_key = api_secret

    def sign_message(self):
        try:
            # signature string
            nonce = f.md5()
            ts = int(time.time())
            sign_str = f'client_id={self.api_key}&nonce={nonce}&ts={ts}'
            # signature method
            digest = hmac.new(bytes(self.client_key, encoding='utf-8'), bytes(sign_str, encoding='utf-8'),
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

    def place_order(self, symbol: str, price: float, quantity: float, side: int):
        try:
            url = self.urlbase + '/open/v1/orders/place'
            params = self.sign_message()
            params.update({
                'symbol': self.symbol_convert(symbol),
                'price': price,
                'quantity': quantity,
                'side': side
            })
            is_ok, content = self.request('POST', url, data=params)
            if is_ok:
                return content
            else:
                self.output('place_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, symbol: str, order_id: str, trade_no: str):
        try:
            url = self.urlbase + '/open/v1/orders/cancel'
            params = self.sign_message()
            params.update({
                'symbol': self.symbol_convert(symbol),
                'order_id': order_id,
                'trade_no': trade_no
            })
            is_ok, content = self.request('POST', url, data=params)
            if is_ok:
                return content
            else:
                self.output('cancel_order', content)
        except Exception as e:
            print(e)

    def cancel_batch_order(self, symbol: str):
        try:
            url = self.urlbase + '/open/v1/orders/batcancel'
            params = self.sign_message()
            params.update({'symbol': self.symbol_convert(symbol)})
            is_ok, content = self.request('POST', url, data=params)
            if is_ok:
                return content
            else:
                self.output('cancel_batch_order', content)
        except Exception as e:
            print(e)

    def last_order(self, symbol: str):
        try:
            url = self.urlbase + '/open/v1/orders/last'
            params = self.sign_message()
            params.update({'symbol': self.symbol_convert(symbol)})
            is_ok, content = self.request('GET', url, params=params)
            if is_ok:
                return content
            else:
                self.output('last_order', content)
        except Exception as e:
            print(e)

    def open_orders(self, symbol: str, pagenum: int = None, pagesize: int = None, side: int = None, start: int = None,
               end: int = None):
        try:
            url = self.urlbase + '/open/v1/orders'
            params = self.sign_message()
            params.update({'symbol': self.symbol_convert(symbol)})

            is_ok, content = self.request('GET', url, params=params)
            if is_ok:
                return content['data']
            else:
                return self.output('open_orders', content)
        except Exception as e:
            print(e)

    def orders_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/open/v1/orders'
            params = self.sign_message()
            params.update({'symbol': self.symbol_convert(symbol), 'order_id': order_id})

            is_ok, content = self.request('GET', url, params=params)
            if is_ok:
                return content
            else:
                self.output('orders_detail', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    hoo = HooAuth('https://api.hoolgd.com', "iJsVEJDESyTXdm8hRBuf79fANdwNB5", "J7EqDCc6FaKA8n5nCy8WJ1uoM4HSZeg2k43mepX5TNjz1qLHUs")
    print(hoo.place_order('EOS_USDT', 1.0016, 11, 1))
    # print(hoo.cancel_order('UMA_USDT', '1', '2'))
    # print(hoo.cancel_batch_order('EOS_USDT'))
    # print(hoo.last_order('BTC_USDT'))
    # print(hoo.open_orders('BTC_USDT'))
    # print(hoo.orders_detail('BTC_USDT', '1'))

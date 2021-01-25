import hashlib
import hmac
import time
import requests
import json
from urllib.parse import urlencode

class YobitAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_message(self, params: dict = None):
        if params is None:
            params = {}
        try:
            # signature string
            params['nonce'] = str(time.time())
            msg = urlencode(params)
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(msg, encoding='utf-8'),
                              digestmod=hashlib.sha512).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        pass

    def cancel_order(self, symbol: str, order_id: str):
        pass

    def cancel_all(self, symbol: str, side: str):
        pass

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        pass

    def order_detail(self, symbol: str, order_id: str):
        pass

    def wallet_balance(self):
        try:
            url = self.urlbase
            data = {
                'method': 'getInfo',
            }
            headers = {
                'Key': self.api_key,
                'Sign': self._sign_message(data),
                'Content-type': 'application/x-www-form-urlencoded'
            }
            resp = requests.post(url, data=data, headers=headers).json()
            balance, frozen = {}, {}
            if resp['success'] == 1:
                wallet = resp["return"]['funds']
                balance = {key: float(value) for key, value in wallet.items()}
            else:
                print(f'Yobit auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Yobit auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = YobitAuth('https://yobit.net/tapi/', '3A7D13AD4F1EB53C0CD68935ABE1AEF5',
                      'a3f933553f2d3949e5485b7fd5985446')
    # print(bit.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.user_trades('BTC_USDT'))
    print(bit.wallet_balance())
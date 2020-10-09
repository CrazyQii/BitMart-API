# -*- coding: utf-8 -*-
"""
授权接口
2020-10-4 hlq
"""

from quoine.quoine_public import QuoinePublic
import jwt
import time
import json


class QuoineAuth(QuoinePublic):
    def __init__(self, urlbase, api_key, api_secret):
        super().__init__(urlbase)
        self.token_id = api_key
        self.user_secret = api_secret

    def sign_message(self, path):
        """ Authentication """
        try:
            payload = {
                'path': path,
                'nonce': round(time.time() * 1000),
                'token_id': self.token_id
            }
            sign = jwt.encode(payload, self.user_secret, algorithm='HS256').decode('ascii')
            return sign
        except Exception as e:
            print(e)

    def place_order(self, order_type: str, product_id: int, side: str, quantity: float, price: float, **kwargs):
        try:
            url = self.urlbase + '/orders/'
            sign_message = self.sign_message(url)
            params = {
                'order': {
                    'order_type': order_type,
                    'product_id': product_id,
                    'side': side,
                    'quantity': quantity,
                    'price': price
                }
            }
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            if kwargs:
                params.update(kwargs)

            is_ok, content = self.request('POST', url, data=json.dumps(params), headers=headers)
            if is_ok:
                return content['id']
            else:
                self.output('place_order', content)
        except Exception as e:
            print(e)

    def get_order(self, id: int):
        try:
            url = self.urlbase + f'/orders/{id}'
            sign_message = self.sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                self.output('get_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, id):
        try:
            url = self.urlbase + f'/orders/{id}/cancel'
            sign_message = self.sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self.request('PUT', url, headers=headers)
            if is_ok:
                return content
            else:
                self.output('cancel_order', content)
        except Exception as e:
            print(e)

    def get_own_executions(self, product_id: int):
        try:
            url = self.urlbase + f'/executions/me?product_id={product_id}'
            sign_message = self.sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                self.output('get_own_executions', content)
        except Exception as e:
            print(e)

    def get_fiat_account(self):
        try:
            url = self.urlbase + '/fiat_accounts'
            sign_message = self.sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                self.output('get_fiat_account', content)
        except Exception as e:
            print(e)

    def create_account(self, currency: str):
        try:
            url = self.urlbase + '/fiat_accounts'
            sign_message = self.sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            params = {"currency": currency}
            is_ok, content = self.request('POST', url, data=json.dumps(params), headers=headers)
            if is_ok:
                return content
            else:
                self.output('create_account', content)
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            url = self.urlbase + '/accounts/balance'
            sign_message = self.sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                self.output('get_account_balance', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    quoine = QuoineAuth('https://api.liquid.com', '1671514', "KD0qrYi5Gsrrai7vAgoA/8597SviZDYTxgx9+NlGd4ikmaboGRBhy5DbJAaQRXcGJaMNaT38lCf6BhsMrSju2Q==")
    # print(quoine.place_order('limit', 5, 'buy', 0.01, 500.0))  # 403 You do not have permission
    # order_id = quoine.place_order('limit', 10000, 'buy', 0.01, 500.0)
    # print(quoine.get_order(1))
    # print(quoine.cancel_order(1))
    # print(quoine.get_fiat_account())
    # print(quoine.get_own_executions(1001232))
    # print(quoine.create_account('JPY'))
    print(quoine.wallet_balance())

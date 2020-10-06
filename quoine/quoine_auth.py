# -*- coding: utf-8 -*-
"""
授权接口
2020-10-4 hlq
"""

from quoine.quoine_public import QuoinePublic
import jwt
import time


class QuoineAuth(QuoinePublic):
    def __init__(self, baseurl, token_id, user_secret):
        super().__init__(baseurl)
        self.token_id = token_id
        self.user_secret = user_secret

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
            print('-----Exception-----')
            return e

    def headers(self, signature):
        """ 请求头 """
        try:
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': signature,
                'Content-Type': 'application/json'
            }
            return headers
        except Exception as e:
            print('-----Exception-----')
            return e

    def place_order(self, order_type: str, product_id: int, side: str, quantity: float, price: float, **kwargs):
        try:
            url = self.baseurl + '/orders/'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            params = {
                'order': {
                    'order_type': order_type,
                    'product_id': product_id,
                    'side': side,
                    'quantity': quantity,
                    'price': price
                }
            }
            if kwargs:
                params.update(kwargs)

            is_ok, content = self.request('POST', url, params=params, headers=headers)
            if is_ok:
                return content['id']
            else:
                return self.output('place_order', content)
        except Exception as e:
            return e

    def get_order(self, id: int):
        try:
            url = self.baseurl + f'/orders/{id}'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                return self.output('get_order', content)
        except Exception as e:
            return e

    def cancel_order(self, id):
        try:
            url = self.baseurl + f'/orders/{id}/cancel'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            is_ok, content = self.request('PUT', url, headers=headers)
            if is_ok:
                return content
            else:
                return self.output('cancel_order', content)
        except Exception as e:
            return e

    def get_own_executions(self, product_id: int):
        try:
            url = self.baseurl + f'/executions/me?product_id={product_id}'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                return self.output('get_own_executions', content)
        except Exception as e:
            return e

    def get_fiat_account(self):
        try:
            url = self.baseurl + '/fiat_accounts'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                return self.output('get_fiat_account', content)
        except Exception as e:
            return e

    def create_account(self, currency: str):
        try:
            url = self.baseurl + '/fiat_accounts'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            params = {"currency": currency}
            is_ok, content = self.request('POST', url, params=params, headers=headers)
            if is_ok:
                return content
            else:
                return self.output('create_account', content)
        except Exception as e:
            return e

    def get_account_balance(self):
        try:
            url = self.baseurl + '/accounts/balance'
            sign_message = self.sign_message(url)
            headers = self.headers(sign_message)
            is_ok, content = self.request('GET', url, headers=headers)
            if is_ok:
                return content
            else:
                return self.output('get_account_balance', content)
        except Exception as e:
            return e


if __name__ == '__main__':
    quoine = QuoineAuth('https://api.liquid.com', '', '')
    print(quoine.place_order('limit', 5, 'buy', 0.01, 500.0))  # 403 You do not have permission
    # order_id = quoine.place_order('limit', 10000, 'buy', 0.01, 500.0)
    # print(quoine.get_order(1))
    # print(quoine.cancel_order(1))
    # print(quoine.get_fiat_account())
    # print(quoine.get_own_executions(1001232))
    # print(quoine.create_account('JPY'))
    # print(quoine.get_account_balance())

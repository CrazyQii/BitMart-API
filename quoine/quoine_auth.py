"""
授权接口
"""

from quoine.quoine_public import QuoinePublic
import hmac
import time
import json
import hashlib


class QuoineAuth(QuoinePublic):
    def __init__(self, baseurl, token_id, user_secret):
        super().__init__(baseurl)
        self.token_id = token_id
        self.user_secret = user_secret

    def signature(self, path):
        """ Authentication """
        payload = {
            'path': path,
            'nonce': round(time.time() * 1000),
            'token_id': self.token_id
        }
        sign = hmac.new(bytes(self.user_secret, encoding='utf-8'), bytes(json.dumps(payload), encoding='utf-8'),
                        digestmod=hashlib.sha256)
        return sign.hexdigest()

    def headers(self, signature):
        """ 请求头 """
        headers = {
            'X-quoine-API-Version', '2',
            'X-quoine-Auth', signature,
            'Content-Type', 'application/json'
        }
        return headers

    def place_order(self, order_type: str, product_id: int, side: str, quantity: str, price: str, **kwargs):
        url = self.baseurl + ' /orders/'
        sign = self.signature(url)
        headers = self.headers(sign)
        params = {
            'order_type': order_type,
            'product_id': product_id,
            'side': side,
            'quantity': quantity,
            'price': price
        }
        [params.update({key, value}) for key, value in kwargs.items()]

        is_ok, content = self.request('POST', url, params=params, headers=headers)
        if is_ok:
            return content
        else:
            return self.output('place_order', content)


if __name__ == '__main__':

    # 没有 API takens
    quoine = QuoineAuth('https://api.liquid.com', '','')
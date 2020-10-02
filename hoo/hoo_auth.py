"""
鉴权接口
"""

from faker import Faker
from hoo import hoo_public
import hmac
import time


f = Faker(locale='zh-CN')


class HooAuth:
    def __init__(self, baseurl, api_key, client_key):
        self.baseurl = baseurl
        self.api_key = api_key
        self.client_key = client_key

    def sign(self):
        try:
            # signature string
            nonce = f.md5()
            ts = round(time.time() * 1000)
            sign_str = f'client_id={self.api_key}&nonce={nonce}&ts={ts}'
            # signature method
            sign = hmac.new(bytes(self.client_key, encoding='utf-8'), bytes(sign_str, encoding='utf-8'),
                            digestmod='sha256')
            return sign.hexdigest()
        except Exception as e:
            print(e)

    



"""
api.py
-------------------
api接口文件
"""
from . import client, const as c


class API:
    def __init__(self, api_key, secret_key, memo):
        self.clients = client.Client(api_key=api_key, secret_key=secret_key, memo=memo)

    # GET https://api-cloud.bitmart.com/spot/v1/currencies
    def get_currencies(self):
        return self.clients.request_without_param('GET', c.API_CURRENCIES_URL)

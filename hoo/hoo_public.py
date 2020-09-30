"""
公共接口
"""
import requests
import traceback


class HooPublic:
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def request(self, method, url, data=None, headers=None):
        try:
            resp = requests.request(method, url, data=data, headers=headers)

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    'path': url,
                    'method': method,
                    'data': data,
                    'code': resp.status_code,
                    'msg': resp.content
                }
                return False, error
        except Exception as e:
            error = {
                'path': url,
                'method': method,
                'data': data,
                'traceback': traceback.format_exc(),
                'error': e
            }
            return False, error

    # https://api.hoolgd.com/open/v1/tickers/market
    def get_tickers_market(self):
        try:
            url = self.baseurl + '/open/v1/tickers/market'
            resp = self.request('GET', url)
            return resp

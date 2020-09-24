"""
api_client.py
----------------
封装请求
"""
from . import api_util, api_const as c
import requests


class Client:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def _request(self, method, req_url, param, auth_type: str, weight):
        """
        handle request to binance api
        """
        # entire url
        url = c.BASE_URL + req_url

        # user authentication and set body
        if auth_type == c.AUTH_NONE:  # None
            headers = api_util.get_header(interval_num=1,
                                          interval_letter=c.IntervalLetter.MINUTE.value,
                                          weight=weight,
                                          api_key=self.api_key, )

        elif auth_type == c.AUTH_KEYED:  # Keyed
            headers = api_util.get_header(interval_num=1,
                                          interval_letter=c.IntervalLetter.MINUTE.value,
                                          weight=weight,
                                          api_key=self.api_key, )
            # 获取服务器时间戳
            rep = requests.get('https://api.binance.com/api/v3/time')
            param['timestamp'] = rep.json()['serverTime']
        else:  # Keyed and Sign
            headers = api_util.get_header(interval_num=1,
                                          interval_letter=c.IntervalLetter.MINUTE.value,
                                          weight=weight,
                                          api_key=self.api_key)
            # 获取服务器时间戳
            rep = requests.get('https://api.binance.com/api/v3/time')
            param['timestamp'] = rep.json()['serverTime']
            # 设置签名到请求参数中
            param['signature'] = api_util.sign(self.secret_key, param)

        print(param)

        # send request
        if method == c.GET:
            # GET 方法的接口, 参数必须在 query string中发送
            response = requests.get(url=url, params=param, headers=headers)
        elif method == c.PUT:
            response = requests.put(url=url, data=param, headers=headers)
        elif method == c.DELETE:
            response = requests.delete(url=url, data=param, headers=headers)
        else:
            response = requests.post(url=url, data=param, headers=headers)
        return response

    def request_with_param(self, method, url, param, auth_type, weight):
        return self._request(method, url, param, auth_type, weight)

    def request_without_param(self, method, url, auth_type, weight):
        return self._request(method, url, {}, auth_type, weight)

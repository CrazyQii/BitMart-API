"""
client.py
----------------
封装请求
"""
from . import util, const as c
from enum import Enum
import requests
import json


class Client:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def _request(self, method, req_url, param, auth_type: str, weight):
        """
        handle request to binance api
        """
        # user authentication and set body
        if auth_type == c.AUTH_NONE:
            headers = util.get_header(interval_num=1,
                                      interval_letter=c.IntervalLetter.MINUTE.value,
                                      weight=weight)

        elif auth_type == c.AUTH_KEYED:
            headers = util.get_header(interval_num=1,
                                      interval_letter=c.IntervalLetter.MINUTE.value,
                                      weight=weight,
                                      api_key=self.api_key,)
        else:
            headers = util.get_header(interval_num=1,
                                      interval_letter=c.IntervalLetter.MINUTE.value,
                                      weight=weight,
                                      api_key=self.api_key)
            # 设置签名到请求参数中
            param['signature'] = util.sign(self.secret_key)

        param['timestamp'] = util.get_timestamp()

        # get and post for url
        if method == c.GET:
            # GET 方法的接口, 参数必须在 query string中发送。
            url = c.BASE_URL + req_url + util.parse_param_to_str(param)
        else:
            url = c.BASE_URL + req_url

        # request body
        # POST, PUT, 和DELETE方法的接口, 在request body中发送。
        body = json.dumps(param) if method == c.POST or method == c.DELETE or method == c.PUT else ''

        # send request
        response = None
        if method == c.GET:
            response = requests.get(url=url, headers=headers)
        elif method == c.PUT:
            response = requests.put(url=url, data=body, headers=headers)
        elif method == c.DELETE:
            response = requests.delete(url=url, data=body, headers=headers)
        else:
            response = requests.post(url=url, data=body, headers=headers)

        return response

    def request_with_param(self, method, url, param, auth_type, weight):
        return self._request(method, url, param, auth_type, weight)

    def request_without_param(self, method, url, auth_type, weight):
        return self._request(method, url, {}, auth_type, weight)

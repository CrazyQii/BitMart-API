"""
client.py
----------------
封装请求
"""
from . import util, const as c
import requests
import json


class Client:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def _request(self, method, req_url, param, auth):
        """ handle request to binance api"""
        # url and param
        if method == c.GET:
            # GET 方法的接口, 参数必须在 query string中发送。
            url = c.BASE_URL + req_url + util.parse_param_to_str(param)
        else:
            url = c.BASE_URL + req_url

        # request body
        # POST, PUT, 和DELETE方法的接口, 在request body中发送。
        body = json.dumps(param) if method == c.POST or method == c.DELETE or method == c.PUT else ''

        # user authentication
        # if auth == c.

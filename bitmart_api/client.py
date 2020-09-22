"""
client.py
-------------------
封装请求，返回数据
"""
from . import const as c, util
from bitmart.cloud_utils import sign, get_timestamp, pre_substring
import requests
import json


class Client:
    def __init__(self,  api_key, secret_key, memo):
        self.api_key = api_key
        self.secret_key = secret_key
        self.memo = memo
        self.base_url = c.BASE_URL

    def _request(self,  method, request_path, param, auth):
        """
        请求方法
        :param request_path: 请求路径
        :param method: 请求方法
        :param param: 请求参数(get)，请求体(post)
        :param auth: 身份认证
        :return:
        """

        # request url
        if method == 'GET':
            url = self.base_url + request_path + util.parse_params_to_str(param)
        else:
            url = self.base_url + request_path

        # post body
        body = json.dumps(param) if method == c.POST else ''

        # client identify authentication(set header)
        if auth is None:
            headers = util.get_header(api_key=None, sign_key=None, timestamp=None)
        elif auth == 'keyed':
            headers = util.get_header(api_key=self.api_key, sign_key=None, timestamp=None)
        else:  # signed
            timestamp = get_timestamp()
            sign_key = sign(pre_substring(timestamp=timestamp, memo=self.memo, body=str(body)), self.secret_key)
            headers = util.get_header(api_key=self.api_key, sign_key=sign_key, timestamp=timestamp)

        # send request
        response = None
        if method == c.GET:
            response = requests.get(url=url, headers=headers)
        else:
            response = requests.post(url=url, data=body, headers=headers)

        # HTTPException
        return response.json()

    def request_with_param(self, method, request_url, param=None, auth=None):
        """ 有参数请求 """
        return self._request(method, request_url, param, auth)

    def request_without_param(self, method, request_url, auth=None):
        """ 无参请求 """
        return self._request(method, request_url, {}, auth)

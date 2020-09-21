"""
Bitmart.util
~~~~~~~~~~~~~~~
工具包，将get和post请求单独提取出来进行封装
"""

from urllib import request
from urllib import parse
from urllib import error
from faker import Faker
from flask import jsonify
from Bitmart.bitmart.api_spot import APISpot
from . import const as c
import requests
import json
import time

f = Faker(locale='zh_CN')


class PostGet:
    """
    POST_GET工具包，对get和post方法进行封装
    """
    __api_key = '0db8cf2de9b3c13c98f947a0229e284dde89e082'
    __secret_key = '6c6c98544461bbe71db2bca4c6d7fd0021e0ba9efc215f9c6ad41852df9d9df9'
    __memo = str(time.time())

    def __init__(self, url, method, data=None, headers=None):
        """
        :param url: 请求路径
        :param method: 请求方法(get / post)
        :param data: POST请求数据
        :param headers: 请求头
        """
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'X-BM-KEY': self.__api_key,
                'X-BM-SIGN': '',
                'X-BM-TIMESTAMP': self.__memo
            }
        self.response = self.send_main(url, method, data, headers)

    def send_main(self, url, method, data, headers):
        """
        主方法: 将POST和GET放到一起
        """
        if method == 'POST' or method == 'post':
            return self.send_post(url, data, headers)
        else:
            return self.send_get(url, data, headers)

    def send_post(self, url, data, headers):
        """
        向 Bitmart 发送POST请求, 返回对应code和message
        """
        req = request.Request(url=url, data=data, headers=headers)
        try:
            with request.urlopen(req) as response:
                print(response)
                print(response.read())
                return json.loads(response.read())
        except error.HTTPError as e:
            return {'code': e.code, 'message': e.reason}

    def send_get(self, url, data, headers):
        """
        向 Bitmart 发送GET请求，返回对应code和message
        """
        # request 对象
        if data is not None:  # 存在请求参数，封装请求url
            url = url + '?' + parse.urlencode(data)
        req = request.Request(url=url, headers=headers)
        # URLError
        try:
            with request.urlopen(req) as response:
                return json.loads(response.read())
        except error.HTTPError as e:
            return {'code': e.code, 'message': e.reason}


class Result:
    """
    响应代码，返回 json 格式的数据
    """

    def __init__(self, code, message, data=None):
        """
        :param code: 响应代码
        :param message: 响应信息
        :param data: 返回数据
        """
        self.result = self.pack_json(code, message, data)

    def pack_json(self, code, message, data):
        """
        封装json格式数据
        data: 数据库中取出的数据
        """
        if code == 1000:
            resp = {
                'code': code,
                'message': message,
                'data': data,
                'trace': f.sha1()
            }
            return jsonify(resp)  # 响应头为 application/json
        else:
            resp = {
                'code': code,
                'message': message,
                'trace': f.sha1()
            }
            return jsonify(resp)


def parse_params_to_str(param):
    """ get请求参数转为字符串 """
    url = '?' + '&'.join([str(key) + '=' + str(value) for key, value in param])
    return url


def get_header(api_key, sign_key, timestamp):
    """ 获取请求头 """
    headers = {
        c.CONTENT_TYPE: c.APPLICATION_JSON,
        c.USER_AGENT: c.VERSION
    }

    if api_key:
        headers[c.API_KEY] = api_key
    if sign_key:
        headers[c.SIGN_KEY] = sign_key
    if timestamp:
        headers[c.TIMESTAMP] = timestamp
    return headers

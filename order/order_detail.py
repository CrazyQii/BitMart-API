# -*- coding: utf-8 -*
"""
asset.cancel_order
~~~~~~~~~~~~~~~~~~
获取订单详情
"""

from Bitmart.util import PostGet
from Bitmart.util import Result


class OrderDetail:
    """ 委托下单 """
    def __init__(self, url, method, req_data=None, headers=None):
        """
        :param url: 请求路径
        :param method: 请求方法
        :param req_data: 请求数据
        :param headers: 请求头
        """
        self.response = self.resp_data(url=url, data=req_data, method=method, headers=headers)

    def resp_data(self, url, data, method, headers):
        response = PostGet(url=url, data=data, method=method, headers=headers).response
        code = response.get('code')
        message = response.get('message')
        data = response.get('data')
        return Result(code, message, data).result


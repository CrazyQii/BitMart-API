# -*- coding: utf-8 -*
"""
public.ticker
~~~~~~~~~~~~~~~~~~
Ticker 是交易对市场状态的概览，包含最新成交价、买一价、卖一价和 24 小时交易量的快照信息
请求Bitmart API（数据库取数）
"""

from Bitmart import util


class Ticker:

    def __init__(self, url, method, req_data=None, headers=None):
        """
        :param url: 请求路径
        :param method: 请求方法
        :param req_data: 请求数据
        :param headers: 请求头
        """
        self.response = self.resp_data(url, method, req_data, headers)

    def resp_data(self, url, method, req_data, headers):
        """ 拉取currency数据，数据逻辑处理 """
        response = util.PostGet(url, method, req_data, headers).response
        # 设置响应信息
        code = response.get('code')
        message = response.get('message')
        resp_data = response.get('data')
        return util.Result(code, message, resp_data).result

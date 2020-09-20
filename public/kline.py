# -*- coding: utf-8 -*
"""
public.kline
~~~~~~~~~~~~~~~~~~
获取指定交易对的指定时间范围内的 k 线数据
"""

from Bitmart import util


class Kline:

    def __init__(self, url, method, req_data=None, headers=None):
        """
        :param url: 请求路径
        :param method: 请求方法
        :param req_data: 请求数据
        :param headers: 请求头
        """
        self.response = self.resp_data(url, method, req_data, headers)

    def resp_data(self, url, method, req_data, headers):
        """ 拉取kline数据，数据逻辑处理 """
        response = util.PostGet(url, method, req_data, headers).response
        # 设置响应信息
        code = response.get('code')
        message = response.get('message')
        resp_data = response.get('data')
        return util.Result(code, message, resp_data).result

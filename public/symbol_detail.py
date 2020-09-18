"""
Bitmart.symbol_detail
~~~~~~~~~~~~~~~~~~~
获取平台所有交易对的详情列表
"""

from Bitmart import util


class SymbolDetail:

    def __init__(self, url, method, req_data=None, headers=None):
        """
        :param url: 请求路径
        :param method: 请求方法
        :param req_data: 请求数据
        :param headers: 请求头
        """
        self.response = self.resp_data(url, method, req_data, headers)

    def resp_data(self, url, method, req_data, headers):
        """ 拉取数据进行逻辑处理 """
        response = util.PostGet(url, method, req_data, headers).response
        # 设置相应信息
        code = response.get('code')
        message = response.get('message')
        data = response.get('data')
        return util.Result(code, message, data).result

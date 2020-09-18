"""
Bitmart.util
~~~~~~~~~~~~~~~
工具包，将get和post请求单独提取出来进行封装
"""

from urllib import request
from urllib import parse
from urllib import error
from faker import Faker
import json

f = Faker(locale='zh_CN')


class PostGet:
    """
    POST_GET工具包，对get和post方法进行封装
    """

    def __init__(self, url, method, data=None, headers=None):
        """
        :param url: 请求路径
        :param method: 请求方法(get / post)
        :param data: 请求数据
        :param headers: 请求头
        """
        if headers is None:
            headers = {'Content-Type': 'application/json'}
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
        发送POST请求, 返回对应code和message
        """
        data = parse.urlencode(data)
        data = data.encode('ascii')
        req = request.Request(url, data, headers)
        try:
            with request.urlopen(req) as response:
                print(response.read())
                return json.loads(response.read())
        except error.HTTPError as e:
            return {'code': e.code, 'message': e.reason}

    def send_get(self, url, data, headers):
        """
        发送GET请求，返回对应code和message
        """
        # request 对象
        if data is not None:
            data = parse.urlencode(data)
            data = data.encode('ascii')
        req = request.Request(url, data, headers)
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
            return json.dumps(resp)
        else:
            resp = {
                'code': code,
                'message': message,
                'trace': f.sha1()
            }
            return json.dumps(resp)

# if __name__ == '__main__':
#     # 模拟请求
#     run = Util('https://api-cloud.bitmart.info/spot/v1/currencies', 'get')
#     print(run.response)
#
#     datas = {
#         "symbol":"BTC_USDT",
#         "side":"buy",
#         "type":"limit",
#         "size":"10",
#         "price":"7000"
#     }
#     run = Util('https://api-cloud.bitmart.info/spot/v1/submit_order', 'post', data=datas)
#     print(run.response)

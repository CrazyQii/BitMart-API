"""
util.py
-------------
工具包
"""
from binance_api import const as c
from enum import Enum
import datetime
import hmac
from faker import Faker

f = Faker(locale='zh-CN')


def sign(secret_key):
    """ 签名 """
    mac = hmac.new(bytes(secret_key, encoding='utf8'), digestmod='sha256')
    return mac.hexdigest()


def get_timestamp():
    """ 获取时间戳 """
    return str(datetime.datetime.now().timestamp() * 1000).split('.')[0]


def parse_param_to_str(param):
    """ 解析get参数格式 """
    url = ''
    if param is not None:
        url = '?' + '&'.join([str(key) + '=' + str(value) for (key, value) in param.items()])
    return url


def get_header(interval_num: int, interval_letter: Enum, weight, api_key=None):
    """ 设置请求头 """
    headers = dict()
    headers[c.CONTENT_TYPE] = c.APPLICATION_JSON
    headers[c.USER_AGENT] = c.VERSION
    # 权重设置
    headers[c.X_MBX_WEIGHT+f'-{str(interval_num)}{interval_letter}'] = str(weight)
    if api_key is not None:
        headers[c.X_MBX_APIKEY] = c.USER_API_KEY
    return headers


def get_new_client_order_id(order_id):
    """ 生成客户订单id """
    if order_id is None:
        return f.sha1()
    else:
        return order_id

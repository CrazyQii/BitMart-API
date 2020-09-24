"""
api_util.py
-------------
工具包
"""
from binance_api import api_const as c
from enum import Enum
import hmac
from faker import Faker

f = Faker(locale='zh-CN')


def sign(secret_key, param):
    """ 签名 """
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(parse_param_to_query_string(param), encoding='utf-8'), digestmod='sha256')
    return mac.hexdigest()


def parse_param_to_query_string(param):
    """ 解析queryString参数格式 """
    query_string = ''
    if param is not None:
        query_string = '&'.join([str(key) + '=' + str(value) for (key, value) in param.items()])
    return query_string


def get_header(interval_num: int, interval_letter: Enum, weight, api_key=None):
    """ 设置请求头 """
    headers = dict()
    headers[c.CONTENT_TYPE] = c.APPLICATION_JSON
    headers[c.USER_AGENT] = c.VERSION
    # 权重设置
    headers[c.X_MBX_WEIGHT+f'-{str(interval_num)}{interval_letter}'] = str(weight)
    if api_key is not None:
        headers[c.X_MBX_APIKEY] = api_key
    return headers


def get_new_client_order_id(order_id):
    """ 生成客户订单id """
    if order_id is None:
        return f.password(length=20, special_chars=False, digits=True)
    else:
        return order_id

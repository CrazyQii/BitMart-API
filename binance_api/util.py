"""
util.py
-------------
工具包
"""
import datetime
import hmac


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

"""
Bitmart.util
~~~~~~~~~~~~~~~
工具包
"""

from . import const as c
import datetime
import hmac


def parse_params_to_str(param):
    """ get请求参数转为字符串 """
    if param is None:
        return ''
    else:
        url = '?' + '&'.join([str(key) + '=' + str(value) for (key, value) in param.items()])
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


def sign(message, secret_key):
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    return mac.hexdigest()


# timestamp + "#" + memo + "#" + queryString
def pre_substring(timestamp, memo, body):
    return f'{str(timestamp)}#{memo}#{body}'


def get_timestamp():
    return str(datetime.datetime.now().timestamp() * 1000).split('.')[0]
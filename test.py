# -*- coding: utf-8 -*
"""
Bitmart.main
~~~~~~~~~~~~~~~
主文件：接收前端请求，初始化server，定义接口函数，程序入口

"""

import sys, os

# 解决命令行import错误问题
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from binance_api import api, const as c
from flask import Flask
from flask import request


# server = Flask(__name__)  # 定义server


# 程序入口
if __name__ == '__main__':
    # server.run(port=7777, debug=True, host='0.0.0.0')  # 执行server
    binance = api.API(c.USER_API_KEY, c.USER_SECRET_KEY)
    print(binance.post_limit_order_test('BTCUSDT', c.Side.BUY.value, c.TimeInForce.GTC.value, 10, 10))

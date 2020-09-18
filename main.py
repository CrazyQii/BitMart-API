# -*- coding: utf-8 -*
"""
Bitmart.main
~~~~~~~~~~~~~~~
主文件：初始化server，定义接口函数，程序入口
"""

import sys, os

# 解决命令行import错误问题
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from Bitmart.public import currency
from Bitmart.public import symbol
from Bitmart.public import symbol_detail
from Bitmart.asset import *
from Bitmart.order import *
from flask import Flask


server = Flask(__name__)  # 定义server

BaseURL = 'https://api-cloud.bitmart.info/spot/v1'  # 请求路由


@server.route('/v1/currencies', methods=['get'])
def currencies():
    """
    定义获取平台所有的加密货币列表接口函数
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "currencies": [
              {
                "id": "BTC",
                "name": "Bitcoin",
                "withdraw_enabled": true,
                "deposit_enabled": true
              },
              {
                "id": "ETH",
                "name": "Ethereum",
                "withdraw_enabled": true,
                "deposit_enabled": true
              }
            ]
          }
        }
    """
    response = currency.Currency(BaseURL+'/currencies', 'get').response
    return response


@server.route('/v1/symbols', methods=['get'])
def symbols():
    """
    获取平台所有的交易对列表
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "symbols": [
               "BMX_ETH",
               "XLM_ETH",
               "MOBI_ETH",
               ...
            ]
          }
        }
    """
    response = symbol.Symbol(BaseURL+'/symbols', 'get').response
    return response


@server.route('/v1/symbols/details', methods=['get'])
def symbols_details():
    """
    获取平台所有交易对的详情列表
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "symbols": [
                {
                    "symbol":"GXC_BTC",
                     "symbol_id":1024,
                     "base_currency":"GXC",
                     "quote_currency":"BTC",
                     "quote_increment":"1.00000000",
                     "base_min_size":"1.00000000",
                     "base_max_size":"10000000.00000000",
                     "price_min_precision":6,
                     "price_max_precision":8,
                     "expiration":"NA",
                     "min_buy_amount":"0.00010000",
                     "min_sell_amount":"0.00010000"
                },
                ...
            ]
          }
        }
    """
    response = symbol_detail.SymbolDetail(BaseURL+'/symbols/details', 'get').response
    return response


# 程序入口
if __name__ == '__main__':
    server.run(port=7777, debug=True, host='0.0.0.0')  # 执行server

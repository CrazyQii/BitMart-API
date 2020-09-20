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

from Bitmart.public import currency
from Bitmart.public import symbol
from Bitmart.public import symbol_detail
from Bitmart.public import ticker
from Bitmart.public import kline
from Bitmart.public import kline_step
from Bitmart.public import depth
from Bitmart.public import trade
from Bitmart.asset import wallet
from Bitmart.order import submit_order
from Bitmart.order import cancel_order
from Bitmart.order import cancel_all_orders
from Bitmart.order import order
from Bitmart.order import order_detail
from Bitmart.order import trade as order_trade
from flask import Flask
from flask import request


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
    response = currency.Currency(BaseURL + '/currencies', 'get').response
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


@server.route('/v1/ticker', methods=['get'])
def tickers():
    """
    获取 Ticker 信息
    :return:
        {
            "message":"OK",
            "code":1000,
            "trace":"6e42c7c9-fdc5-461b-8fd1-b4e2e1b9ed57",
            "data":{
                "tickers":[
                    {
                        "symbol":"BTC_USDT",
                        "last_price":"1.00",
                        "quote_volume_24h":"201477650.88000",
                        "base_volume_24h":"25186.48000",
                        "high_24h":"8800.00",
                        "low_24h":"1.00",
                        "open_24h":"8800.00",
                        "close_24h":"1.00",
                        "best_ask":"0.00",
                        "best_ask_size":"0.00000",
                        "best_bid":"0.00",
                        "best_bid_size":"0.00000",
                        "fluctuation":"-0.9999",
                        "url":"https://www.bitmart.com/trade?symbol=BTC_USDT"
                    }
                ]
            }
        }
    """
    param = request.args
    response = ticker.Ticker(BaseURL+'/ticker', 'get', req_data=param).response
    return response


@server.route('/v1/steps', methods=['get'])
def steps():
    """
    获取平台支持的全部 k 线周期，用分钟表示，最小 1 分钟。
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "steps": [1, 3, 5, 15, 30, 45, 60, 120, 180, 240, 1440, 10080, 43200]
          }
        }
    """
    param = request.args
    response = kline_step.KlineStep(BaseURL+'/steps', 'get', req_data=param).response
    return response


@server.route('/v1/symbols/kline', methods=['get'])
def klines():
    """
    获取指定交易对的指定时间范围内的 k 线数据。
    :return:
        {
            "message":"OK",
            "code":1000,
            "trace":"ae7ede4c-04a3-4004-bd8b-022a12d17e45",
            "data":{
                "klines":[
                    {
                        "timestamp":1590969600,
                        "open":"1.2400000000",
                        "high":"1.2400000000",
                        "low":"1.2000000000",
                        "close":"1.2000000000",
                        "last_price":"1.2000000000",
                        "volume":"4.9000000000"
                    }
                ]
            }
        }
    """
    param = request.args
    response = kline.Kline(BaseURL+'/symbols/kline', 'get', req_data=param).response
    return response


@server.route('/v1/symbols/book', methods=['get'])
def depths():
    """
    获取指定交易对的指定时间范围内的 k 线数据。
    :return:
        {
            "message":"OK",
            "code":1000,
            "trace":"ae7ede4c-04a3-4004-bd8b-022a12d17e45",
            "data":{
                "klines":[
                    {
                        "timestamp":1590969600,
                        "open":"1.2400000000",
                        "high":"1.2400000000",
                        "low":"1.2000000000",
                        "close":"1.2000000000",
                        "last_price":"1.2000000000",
                        "volume":"4.9000000000"
                    }
                ]
            }
        }
    """
    param = request.args
    response = depth.Depth(BaseURL+'/symbols/book', 'get', req_data=param).response
    return response


@server.route('/v1/symbols/trades', methods=['get'])
def trades():
    """
    获取指定交易对的最近成交记录。
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "trades": [
               {
                  "amount":"0.05768509",
                  "order_time":1527057452000,
                  "price":"0.004811",
                  "count":"11.99",
                  "type":"buy"
               },
               ...
            ]
          }
        }
    """
    param = request.args  # get请求参数
    response = trade.Trade(BaseURL+'/symbols/trades', 'get', req_data=param).response
    return response


@server.route('/v1/wallet', methods=['get'])
def wallets():
    """
    获取用户所有币种钱包余额。
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "wallet": [
                 {
                      "id": "BTC",
                      "available": "10.000000",
                      "name": "Bitcoin",
                      "frozen": "10.000000",
                  },
                  ...
            ]
          }
        }
    """
    # 请求头
    headers = {
        'Content-type': str(request.headers.get('Content-type')),
        'X-BM-KEY': str(request.headers.get('X-BM-KEY')),
        'X-BM-SIGN': str(request.headers.get('X-BM-SIGN')),
        'X-BM-TIMESTAMP': str(request.headers.get('X-BM-TIMESTAMP'))
    }
    response = wallet.Wallet(BaseURL+'/wallet', 'get', headers=headers).response
    return response


@server.route('/v1/submit_order', methods=['post'])
def submit_orders():
    """
    获取用户所有币种钱包余额。
    :param:
    {
        "symbol":"BTC_USDT",
        "side":"buy",
        "type":"limit",
        "size":"10",
        "price":"7000"
    }
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
            "order_id":1223181
          }
        }
    """
    param = request.get_data()
    # 请求头
    headers = {
        'Content-type': str(request.headers.get('Content-type')),
        'X-BM-KEY': str(request.headers.get('X-BM-KEY')),
        'X-BM-SIGN': str(request.headers.get('X-BM-SIGN')),
        'X-BM-TIMESTAMP': str(request.headers.get('X-BM-TIMESTAMP'))
    }
    response = submit_order.SubmitOrder(BaseURL+'/submit_order', 'post', req_data=param, headers=headers).response
    return response


@server.route('/v1/cancel_order', methods=['post'])
def cancel_orders():
    """
    取消一个未完成的订单
    :param:
    {
      "symbol":"BTC_USDT",
      "side":"buy"
    }
    :return:
        {
          "code": 1000,
          "trace":"886fb6ae-456b-4654-b4e0-d681ac05cea1",
          "message": "OK",
          "data": {
          }
        }
    """
    param = request.get_data()
    # 请求头
    headers = {
        'Content-type': str(request.headers.get('Content-type')),
        'X-BM-KEY': str(request.headers.get('X-BM-KEY')),
        'X-BM-SIGN': str(request.headers.get('X-BM-SIGN')),
        'X-BM-TIMESTAMP': str(request.headers.get('X-BM-TIMESTAMP'))
    }
    response = cancel_order.CancelOrder(BaseURL+'/cancel_order', 'post', req_data=param, headers=headers).response
    return response


@server.route('/v1/order_detail', methods=['get'])
def order_detail():
    """
    获取订单详情
    :param: https://api-cloud.bitmart.com/spot/v1/order_detail?symbol=BTC_USDT&order_id=1736871726781
    :return:
        {
            "message":"OK",
            "code":1000,
            "trace":"a27c2cb5-ead4-471d-8455-1cfeda054ea6",
            "data":{
                "order_id":1736871726781,
                "symbol":"BTC_USDT",
                "create_time":1591096004000,
                "side":"sell",
                "type":"market",
                "price":"0.00",
                "price_avg":"0.00",
                "size":"0.02000",
                "notional":"0.00000000",
                "filled_notional":"0.00000000",
                "filled_size":"0.00000",
                "status":"8"
            }
        }
    """
    param = request.args
    # 请求头
    headers = {
        'Content-type': str(request.headers.get('Content-type')),
        'X-BM-KEY': str(request.headers.get('X-BM-KEY')),
        'X-BM-SIGN': str(request.headers.get('X-BM-SIGN')),
        'X-BM-TIMESTAMP': str(request.headers.get('X-BM-TIMESTAMP'))
    }
    response = order_detail.OrderDetail(BaseURL+'/order_detail', 'get', req_data=param, headers=headers).response
    return response


@server.route('/v1/orders', methods=['get'])
def orders():
    """
    获取用户订单列表
    :param: https://api-cloud.bitmart.com/spot/v1/orders?symbol=BTC_USDT&status=1&offset=1&limit=100
    :return:
        {
            "message":"OK",
            "code":1000,
            "trace":"70e7d427-7436-4fb8-8cdd-97e1f5eadbe9",
            "data":{
                "current_page":1,
                "orders":[
                    {
                        "order_id":2147601241,
                        "symbol":"BTC_USDT",
                        "create_time":1591099963000,
                        "side":"sell",
                        "type":"limit",
                        "price":"9000.00",
                        "price_avg":"0.00",
                        "size":"1.00000",
                        "notional":"9000.00000000",
                        "filled_notional":"0.00000000",
                        "filled_size":"0.00000",
                        "status":"4"
                    }
                ]
            }
        }
    """
    param = request.args
    # 请求头
    headers = {
        'Content-type': str(request.headers.get('Content-type')),
        'X-BM-KEY': str(request.headers.get('X-BM-KEY')),
        'X-BM-SIGN': str(request.headers.get('X-BM-SIGN')),
        'X-BM-TIMESTAMP': str(request.headers.get('X-BM-TIMESTAMP'))
    }
    response = order.Order(BaseURL+'/orders', 'get', req_data=param, headers=headers).response
    return response


@server.route('/v1/trades', methods=['get'])
def trades():
    """
    获取用户订单列表
    :param: https://api-cloud.bitmart.com/spot/v1/trades?symbol=BTC_USDT&limit=10&offset=1
    :return:
        {
            "message":"OK",
            "code":1000,
            "trace":"a06a5c53-8e6f-42d6-8082-2ff4718d221c",
            "data":{
                "current_page":1,
                "trades":[
                    {
                        "detail_id":256348632,
                        "order_id":2147484350,
                        "symbol":"BTC_USDT",
                        "create_time":1590462303000,
                        "side":"buy",
                        "fees":"0.00001350",
                        "fee_coin_name":"BTC",
                        "notional":"88.00000000",
                        "price_avg":"8800.00",
                        "size":"0.01000",
                        "exec_type":"M"
                    },
                    ...
                ]
            }
        }
    """
    param = request.args
    # 请求头
    headers = {
        'Content-type': str(request.headers.get('Content-type')),
        'X-BM-KEY': str(request.headers.get('X-BM-KEY')),
        'X-BM-SIGN': str(request.headers.get('X-BM-SIGN')),
        'X-BM-TIMESTAMP': str(request.headers.get('X-BM-TIMESTAMP'))
    }
    response = order_trade.Trade(BaseURL+'/trades', 'get', req_data=param, headers=headers).response
    return response


# 程序入口
if __name__ == '__main__':
    server.run(port=7777, debug=True, host='0.0.0.0')  # 执行server
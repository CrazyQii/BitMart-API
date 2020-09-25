# -*- coding: utf-8 -*
"""
test.py
~~~~~~~~~~~~~~~
测试接口

"""
from binance_api.api_const import *
from binance_api import api


# 程序入口
if __name__ == '__main__':
    binance = api.API(USER_API_KEY, USER_SECRET_KEY)

    # 测试
    # ping 服务
    # print(binance.get_ping())
    # print(binance.get_exchange_info().json())

    print('-'*25)

    # test /api/v3/order/test

    # Trade type:limit
    # rep = binance.post_order(symbol="BTCUSDT", side=BUY, type=LIMIT, time_in_force=GTC, quantity=0.1, price=10000)
    # {'code': -2010, 'msg': 'Account has insufficient balance for requested action.'}

    # Trade type:market
    # rep = binance.post_order(symbol="BTCUSDT", side=BUY, type=MARKET, quantity=0.1)
    # {'code': -2010, 'msg': 'Account has insufficient balance for requested action.'}

    # Get order
    # rep = binance.get_order(symbol="BTCUSDT", order_id=2131, orig_client_order_id=None)
    # {'code': -2013, 'msg': 'Order does not exist.'}

    # Get all order
    # rep = binance.get_all_order(symbol="BTCUSDT")

    # 账户信息
    rep = binance.get_account()

    print(rep.json())


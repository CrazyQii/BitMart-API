# -*- coding: utf-8 -*
"""
order.submit_order
~~~~~~~~~~~~~~~~~~~
模拟委托下单
"""

from faker import Faker
import random

f = Faker(locale='zh_CN')


def submit_order(data):
    """ 生成委托下单数据 """
    if data['symbol'] in ['BMX_ETH', 'BMX_BTC', 'BMX_ABC']:
        if data['side'] in ['buy', 'sell'] and data['type'] in ['limit', 'market'] and data['size'] is not None and data['price'] is not None:
            return f.random_number(digits=10)
    else:
        return 0

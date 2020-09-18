# -*- coding: utf-8 -*
"""
public.trades
~~~~~~~~~~~~~~
模拟指定交易对最近成交记录
"""

from faker import Faker
import random

f = Faker(locale='zh_CN')


def trade(para_symbol):
    """ 判断交易对，生成成交记录 """
    para_symbol = str(para_symbol)
    trades = []
    if para_symbol in ['BMX_ETH', 'BMX_BTC', 'BMX_ABC']:
        num = random.randint(2, 10)
        for i in range(num):
            mock = {
                'amount': f.pyfloat(left_digits=2, right_digits=8, positive=True),
                'order_time': f.unix_time(),
                'price': f.pyfloat(left_digits=2, right_digits=8, positive=True),
                'type': f.random_letter()
            }
            trades.append(mock)
        return trades
    else:
        return trades

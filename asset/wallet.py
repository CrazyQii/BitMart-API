# -*- coding: utf-8 -*
"""
asset.wallet
~~~~~~~~~~~~~~~~~~
获取用户所有币种钱包余额
"""

from urllib import request
import json


class Wallet:
    """ 钱包对象 """
    # def __init__(self, id, available, name, frozen):
    #     self.id = id
    #     self.available = available
    #     self.name = name
    #     self.frozen = frozen

    def get_wallet(self):
        """ 获取钱包余额数据 """
        data = request.urlopen('https://api-cloud.bitmart.info/spot/v1/currencies')
        for line in data:
            json_line = json.loads(line)

            print()
            return line


x = Wallet()
x.get_wallet()

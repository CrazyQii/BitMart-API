#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from client import client
from threading import Thread
import logging
import time


# 创建日志对象
def get_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s', "%Y-%m-%d %H:%M:%S")
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    return logging.getLogger(logger_name)


def client1():
    logger1 = get_logger('client1', 'client1.log')
    for item in client.receiver('PAX_USDT', 'kline', 'binance'):
        logger1.info(item)


# def client2():
#     logger2 = get_logger('client2', 'client2.log')
#     for item in client.receiver('ETH_USDT', 'kline'):
#         logger2.info(item)
#
#
# def client3():
#     logger3 = get_logger('client3', 'client3.log')
#     for item in client.receiver('ETH_BTC', 'price'):
#         logger3.info(item)
#
#
# def client4():
#     logger4 = get_logger('client4', 'client4.log')
#     for item in client.receiver('BTC_USDT', 'kline'):
#         logger4.info(item)
#
#
# def client5():
#     logger5 = get_logger('client5', 'client5.log')
#     for item in client.receiver('XRP_USDT', 'orderbook'):
#         logger5.info(item)


if __name__ == '__main__':
    # 多线程模拟客户端
    Thread(target=client1).start()
    # time.sleep(5)
    # Thread(target=client2).start()
    # time.sleep(5)
    # Thread(target=client3).start()
    # time.sleep(5)
    # Thread(target=client4).start()
    # time.sleep(5)
    # Thread(target=client5).start()

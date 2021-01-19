#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from wss.binance_websocket import BinanceWs
from wss.okex_websocket import OkexWs
from wss.huobi_websocket import HuobiWs
from wss.wootrade_websocket import WootradeWs
from threading import Thread
from cacheout import Cache
import redis                    
import time
import json
import logging


class Server(Thread):
    def __init__(self):
        super().__init__()
        self.channels = []  # save subscribed channels
        self.gateways = {'binance': BinanceWs, 'okex': OkexWs, 'huobi': HuobiWs, 'wootrade': WootradeWs}  # class of exchanges
        self.ongoing_gateway = {}  # has been instantiated exchanges
        self.feature = ['price', 'orderbook', 'trade', 'kline', 'order', 'wallet']
        self.cache = Cache(maxsize=256, timer=time.time)
        self.server = redis.StrictRedis(host='localhost', port=6379)  # redis server
        LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        DATE_FORMAT = '%m/%d/%Y %H:%M:%S %p'
        logging.basicConfig(filename='server.log', level=logging.WARNING, format=LOG_FORMAT, datefmt=DATE_FORMAT)
        Thread(target=self.receiver).start()
        Thread(target=self.publisher).start()

    def _integrate_gateway(self, gateway, symbol: str, feature: str):
        try:
            # call the correspond function
            switch = {
                'price': gateway.sub_price,
                'orderbook': gateway.sub_orderbook,
                'trade': gateway.sub_trade,
                'kline': gateway.sub_kline,
                'order': gateway.sub_order,
                'wallet': gateway.sub_wallet_balance
            }
            switch.get(feature, lambda r: print(f'{feature} feature dose not exist!'))(symbol)
        except Exception as e:
            logging.error(f'Integrate gateway error: {e}')

    def _handle_receiver(self):
        try:
            # get sub request from redis key
            recv = self.server.get('sub')
            if recv:
                recv = json.loads(recv)
                # print(recv)
                for item in recv:
                    if item not in self.channels:
                        gateway, symbol, feature = item.split('&')
                        # Determine whether the exchange exists,
                        # if not, return an error,
                        # if it exists, instantiate the exchange
                        if gateway in self.gateways:
                            # Determine whether the exchange has been instantiated
                            if gateway not in self.ongoing_gateway:
                                instant_gate = self.gateways[gateway]()
                                self.ongoing_gateway.update({
                                    gateway: instant_gate
                                })
                            self._integrate_gateway(self.ongoing_gateway[gateway], symbol, feature)
                            # add channel
                            self.channels.append(item)
                        else:
                            msg = f'{gateway} does not exist'
                            data = {
                                'code': 500,
                                'data': None,
                                'msg': msg
                            }
                            self.server.publish(channel=json.dumps(recv), message=json.dumps(data))
                self.server.delete('sub')
        except Exception as e:
            logging.error(f'handle receiver error: {e}')

    def receiver(self):
        try:
            while True:
                time.sleep(2)
                # receive subscription request every 2 seconds
                if self.server.exists('sub'):
                    self._handle_receiver()
        except Exception as e:
            logging.error(f'receiver error: {e}')

    def publisher(self):
        try:
            while True:
                time.sleep(0.001)
                for channel in self.channels:
                    gateway, symbol, feature = channel.split('&')
                    data = self.ongoing_gateway[gateway].data[symbol][feature]
                    # print(data)
                    # if ticker does not existed or exchange server error
                    if data is None or len(data) == 0:
                        data = f'{gateway}&{symbol}&{feature} does not exist'
                    # set cache, determine the duplicate data
                    cache_data = self.cache.get(f'{gateway}&{symbol}&{feature}')
                    if cache_data is None:
                        # cache data does not exist, update cache data and set effective time to 5 seconds
                        if feature == 'kline' and type(data) == list and len(data) > 0:
                            self.cache.set(f'{gateway}&{symbol}&{feature}', data[0], ttl=15)
                        else:
                            self.cache.set(f'{gateway}&{symbol}&{feature}', data, ttl=15)
                    else:
                        if data == cache_data:  # trade / orderbook / price
                            data = {
                                'code': 403,
                                'data': data,
                                'msg': 'Duplicate Data'
                            }
                            self.server.publish(channel=json.dumps(channel), message=json.dumps(data))
                            continue
                        elif type(data) == list and data[0] == cache_data:  # kline
                            data = {
                                'code': 403,
                                'data': data,
                                'msg': 'Duplicate Data'
                            }
                            self.server.publish(channel=json.dumps(channel), message=json.dumps(data))
                        else:  # if the new data differ from cache data, update cache data
                            if feature == 'kline' and len(data) > 0:
                                self.cache.set(f'{gateway}&{symbol}&{feature}', data[0], ttl=15)
                            else:
                                self.cache.set(f'{gateway}&{symbol}&{feature}', data, ttl=15)
                            data = {
                                'code': 200,
                                'data': data,
                                'msg': 'OK'
                            }
                            self.server.publish(channel=json.dumps(channel), message=json.dumps(data))
        except Exception as e:
            logging.error(f'Publisher error: {e}')


if __name__ == '__main__':
    Server()

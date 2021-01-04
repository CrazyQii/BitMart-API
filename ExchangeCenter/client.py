#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from threading import Thread
import redis
import json
import logging


class Client(Thread):
    def __init__(self):
        super().__init__()
        self.server = redis.StrictRedis(host='localhost', port=6379)
        self.start_time = None  # record the start time when

    def subscribe(self, gateway, symbol, feature):
        try:
            channel = f'{gateway}&{symbol}&{feature}'
            # save channel request to redis database
            params = [channel]
            self.server.set('sub', json.dumps(params))
            # subscribe
            pub = self.server.pubsub()
            pub.subscribe(json.dumps(channel))

            error_time = 0
            for recv in pub.listen():
                if error_time > 10000:
                    logging.error('Data does not exist')
                    return
                if recv['type'] == 'message':
                    data = json.loads(recv['data'])
                    if data['code'] == 200:
                        error_time = 0
                        yield data
                    elif data['code'] == 403 or data['']:  # duplicate response or ticker error
                        error_time += 1
                    else:
                        error_time += 1
                else:
                    print(recv)
        except Exception as e:
            logging.error(f'client subscribe error: {e}')

    def receiver(self, symbol, feature, gateway=None):
        try:
            if gateway is None:
                for gateway in ['binance', 'okex', 'huobi', 'wootrade']:
                    for data in self.subscribe(gateway, symbol, feature):
                        yield data
            elif isinstance(gateway, list):
                for gateway in gateway:
                    for data in self.subscribe(gateway, symbol, feature):
                        yield data
            elif isinstance(gateway, str):
                for data in self.subscribe(gateway, symbol, feature):
                    yield data
            else:
                raise Exception('args format error!!')
        except Exception as e:
            logging.error(f'Receiver error: {e}')


client = Client()


# if __name__ == '__main__':
#     client = Client()
#     for i in client.receiver('BT_USDT', 'kline', 'wootrade'):
#         print(i)

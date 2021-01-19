#!/usr/bin/python3
# -*- coding: utf-8 -*-
from threading import Thread, enumerate
from collections import defaultdict
import websocket
import json
import time
import requests
import logging


class BitmartWss(Thread):
    def __init__(self, urlbase=None, api_key=None, api_secret=None, passphrase=None):
        super().__init__()

    def _connect(self, private: bool):
        ws = None
        times = 0
        while True:
            try:
                time.sleep(1)
                logging.info('Binance start to connect ' + self.urlbase)
                ws = websocket.create_connection(self.urlbase)
            except Exception as e:
                logging.error(f'Binance connect error: {e}')
                time.sleep(3)
                times = times + 1
                if times >= 5:
                    logging.error(f'Binance has connected {times} times, and connection end!!!')
                    break
            else:
                break
        return ws

if __name__ == '__main__':
    bm = BitmartWss()


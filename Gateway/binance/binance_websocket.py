#!/usr/bin/python3
# -*- coding: utf-8 -*-
from threading import Thread, enumerate
from collections import defaultdict
import websocket
import json
import time
import requests
import logging


class BinanceWs(Thread):
    def __init__(self, urlbase=None, api_key=None, api_secret=None, passphrase=None):
        super().__init__()
        if urlbase is None:
            self.urlbase = 'wss://stream.binance.com:9443/stream'
        else:
            self.urlbase = urlbase
        if api_key is None:
            self.api_key = 'peHvRKu7QGVZIezAlZfIAhmK5zPxa5ptLo6kkMOLGeJpD1UJhpufUVY6WvYqrDrh'
        else:
            self.api_key = api_key
        self._init_container()

    def _init_container(self):
        self.rest_url = 'https://api.binance.com/api/v3/userDataStream'
        self.channel = []  # record subscribed channel
        self.data = defaultdict(dict)  # record lasted data
        self.SUB_ID = 0  # start to subscribe id
        self.STOP_ID = 1  # stop subscribing id
        self.lastUpdateId = None  # latest orderbook id
        self.listenKey = None  # listenKey
        self.ws = self._connect(private=False)  # create connection with ws
        self.wss = self._connect(private=True)
        self.on_message()

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _sign_message(self):
        def _sign():
            while True:
                try:
                    resp = requests.post(self.rest_url, headers={'X-MBX-APIKEY': self.api_key})
                    if resp.status_code == 200:
                        self.listenKey = resp.json()['listenKey']
                        # keep listenkey alive every 30min
                        time.sleep(1800)
                    else:
                        logging.error(f'Binance cannot get listenKey: {resp.json()}')
                        break
                except Exception as e:
                    logging.error(f'Binance sign message error: {e}')
                    break
        Thread(target=_sign).start()

    def _connect(self, private: bool):
        ws = None
        times = 0
        while True:
            try:
                if private:
                    self._sign_message()
                    time.sleep(1)
                    if self.listenKey is None:
                        raise Exception('ListenKey is None')
                    urlbase = f'{self.urlbase}?streams={self.listenKey}'
                    logging.info('Binance start to connect ' + urlbase)
                    ws = websocket.create_connection(urlbase)
                else:
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

    def _stop(self, channel):
        try:
            params = {
                'method': 'UNSUBSCRIBE',
                'params': [channel],
                'id': self.STOP_ID
            }
            self.ws.send(json.dumps(params))
        except Exception as e:
            logging.error(f'Binance stop channel error: {e}')

    def _sub(self, channel):
        try:
            params = {
                'method': 'SUBSCRIBE',
                'params': [channel],
                'id': self.SUB_ID
            }
            self.ws.send(json.dumps(params))
        except Exception as e:
            logging.error(f'Binance start channel error: {e}')

    # format data
    def _get_kline(self, params: dict, limit=500):
        try:
            ticker = params['stream'].split('@')[0].upper()  # ticker
            params = params['data']
            kline = {
                'timestamp': round(params['E'] / 1000),
                'volume': float(params['k']['v']),
                'open': float(params['k']['o']),
                'last_price': float(params['k']['c']),
                'low': float(params['k']['l']),
                'high': float(params['k']['h'])
            }
            # traverse the data with symbol
            for key, value in self.data.items():
                if ''.join(key.split('_')) == ticker:
                    if len(value['kline']) > limit:  # determine if it exceeds 500
                        value['kline'].pop()
                    value['kline'].insert(0, kline)
                    break
        except Exception as e:
            logging.error(f'Binance get kline error: {e}')

    def _get_trade(self, params: dict):
        try:
            ticker = params['stream'].split('@')[0].upper()  # ticker
            params = params['data']  # data
            trade = {
                'count': float(params['q']),
                'order_time': round(params['E'] / 1000),
                'price': float(params['p']),
                'amount': float(params['q']) * float(params['p']),
                'type': 'sell' if params['m'] else 'buy'
            }
            # traverse the data with symbol
            for key, value in self.data.items():
                if ''.join(key.split('_')) == ticker:
                    value['trade'] = trade
                    value['price'] = {
                        'price': trade['price'],
                        'timestamp': trade['order_time']
                    }
        except Exception as e:
            logging.error(f'Binance get trade error: {e}')

    def _get_orderbook(self, params: dict):
        try:
            ticker = params['stream'].split('@')[0].upper()
            params = params['data']
            if params['lastUpdateId'] == self.lastUpdateId:
                orderbook = None
            else:
                self.lastUpdateId = params['lastUpdateId']  # record the latest orderbook id from binance
                orderbook = {'buys': [], 'sells': []}
                total_amount_buys = 0
                total_amount_sells = 0
                for item in params['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': 1
                    })
                for item in params['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': 1
                    })
            # traverse the data with symbol
            for key, value in self.data.items():
                if ''.join(key.split('_')) == ticker:
                    value['orderbook'] = orderbook
        except Exception as e:
            logging.error(f'Binance get orderbook error: {e}')

    def _get_order(self, params: dict, status=None, limit=200):
        if status is None:
            status = ['NEW', 'TRADE']
        try:
            if params['X'] in status:
                order = {
                    'order_id': params['i'],
                    'symbol': params['s'],
                    'price': float(params['p']),
                    'amount': float(params['q']),
                    'side': params['S'],
                    'price_avg': float(float(params['p']) / float(params['q'])),
                    'filled_amount': float(params['z']),
                    'status': params['X'],
                    'create_time': round(params['O'] / 1000),
                }
                # traverse the data with symbol
                for key, value in self.data.items():
                    if ''.join(key.split('_')) == order['symbol']:
                        # change symbol 'btcusdt' to ''BTC_USDT
                        order['symbol'] = key
                        # index: record the position of an existing order
                        # exist: an existing flag
                        index, exist = 0, False
                        for item in value['order']:
                            # update an existing order
                            if item['create_time'] == order['create_time']:
                                value['order'][index] = order
                                exist = True
                                break
                            index = index + 1
                        if not exist:
                            if len(value['order']) > limit:
                                value['order'].pop()
                            value['order'].insert(0, order)
        except Exception as e:
            logging.error(f'Binance get order error: {e}')

    def _get_wallet_balance(self, params: dict):
        try:
            for row in params['B']:
                if row['a'] in self.data['wallet']:
                    self.data['wallet']['a'].update({
                        'balance': row['f'],
                        'frozen': row['l']
                    })
        except Exception as e:
            logging.error(f'Binance get wallet error: {e}')

    # main function
    def on_message(self):
        def _message():
            try:
                if self.ws is None:
                    logging.error('Binance public does not connected, and connection closed!')
                    return
                while True:
                    recv = json.loads(self.ws.recv())
                    if 'stream' in recv:  # response of data
                        stream = '@'.join(recv['stream'].split('@')[1:])
                        switch = {
                            'trade': self._get_trade,
                            'kline_1m': self._get_kline,
                            'depth20@100ms': self._get_orderbook,
                        }
                        switch.get(stream, lambda r: logging.info(r))(recv)
                    elif recv['id'] == self.SUB_ID:  # response of subscribe successfully
                        recv = {
                            'code': 200,
                            'id': self.SUB_ID,
                            'data': 'ok',
                            'msg': 'Binance sub completely!'
                        }
                        logging.info(recv)
                    elif recv['id'] == self.STOP_ID:  # response of stop successfully
                        recv = {
                            'code': 200,
                            'id': self.STOP_ID,
                            'data': 'ok',
                            'msg': 'Binance stop sub completely!'
                        }
                        logging.info(recv)
                    else:
                        logging.info(recv)
            except Exception as e:
                logging.error(f'Binance Sub error {e}: try to connect again')
                self.ws = self._connect(private=False)
                self._sub(','.join(self.channel))
                _message()

        def _auth_message():
            try:
                if self.wss is None:
                    logging.error('Binance auth does not connected, and connection closed!')
                    return
                while True:
                    recv = json.loads(self.wss.recv())
                    # print(recv)
                    if recv['e'] == 'outboundAccountPosition':
                        self._get_wallet_balance(recv)
                    elif recv['e'] == 'balanceUpdate':
                        logging.info(recv)
                    elif recv['e'] == 'executionReport':
                        self._get_order(recv)
                    else:
                        logging.info(recv)
            except Exception as e:
                logging.error(f'Binance Sub auth error {e}: try to connect again')
                self.ws = self._connect(private=False)
                self._sub(','.join(self.channel))
                self.on_message()

        Thread(target=_message).start()
        # Thread(target=_auth_message).start()

    # subscribe
    def sub_price(self, symbol: str):
        self.data[symbol]['price'] = None
        self.sub_trade(symbol)

    def sub_kline(self, symbol: str):
        self.data[symbol]['kline'] = []
        self.channel.append(f'{self._symbol_convert(symbol)}@kline_1m')
        self._sub(f'{self._symbol_convert(symbol)}@kline_1m')

    def sub_orderbook(self, symbol: str):
        self.data[symbol]['orderbook'] = None
        self.channel.append(f'{self._symbol_convert(symbol)}@depth20@100ms')
        self._sub(f'{self._symbol_convert(symbol)}@depth20@100ms')

    def sub_trade(self, symbol: str):
        self.data[symbol]['trade'] = None
        self.channel.append(f'{self._symbol_convert(symbol)}@trade')
        self._sub(f'{self._symbol_convert(symbol)}@trade')

    # subscribe account
    def sub_wallet_balance(self, symbol: str):
        self.data['wallet'] = {
            symbol.split("_")[0]: {
                'balance': None,
                'frozen': None
            },
            symbol.split("_")[1]: {
                'balance': None,
                'frozen': None
            }
        }

    def sub_order(self, symbol: str):
        self.data[symbol]['order'] = []

    # stop subscribing
    def stop_kline(self, symbol: str):
        channel = f'{self._symbol_convert(symbol)}@kline_1m'
        if channel in self.channel:
            self.channel.remove(channel)
        self._stop(channel)

    def stop_orderbook(self, symbol: str):
        channel = f'{self._symbol_convert(symbol)}@depth20@100ms'
        if channel in self.channel:
            self.channel.remove(channel)
        self._stop(channel)

    def stop_trade(self, symbol: str):
        channel = f'{self._symbol_convert(symbol)}@trade'
        if channel in self.channel:
            self.channel.remove(channel)
        self._stop(channel)


if __name__ == '__main__':
    b = BinanceWs()
    b.sub_trade('BTC_USDT')
    # b.sub_kline('XPO_USDT')

    while True:
        time.sleep(2)
        print(b.data)

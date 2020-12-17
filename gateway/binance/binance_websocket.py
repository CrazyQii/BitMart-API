#!/usr/bin/python3
from threading import Thread
from collections import defaultdict
import websocket
import json
import time
import requests


class BinanceWs(Thread):
    def __init__(self, urlbase, api_key, api_secret=None, passphrase=None):
        super().__init__()
        self.urlbase = urlbase
        self.api_key = api_key
        self._init_container()

    def _init_container(self):
        self.channel = []               # record subscribed channel
        self.data = defaultdict(dict)   # record lasted data
        self.SUB_ID = 0                 # start to subscribe id
        self.STOP_ID = 1                # stop subscribing id
        self.listenKey = None           # listenKey
        self.ws = self._connect()       # create connection with ws
        self.wss = self._connect(private=True)
        self.on_message()               # keep receiving data

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _sign_message(self):
        def sign():
            try:
                while True:
                    urlbase = 'https://api.binance.com/api/v3/userDataStream'
                    resp = requests.post(urlbase, headers={'X-MBX-APIKEY': self.api_key})
                    if resp.status_code == 200:
                        self.listenKey = resp.json()['listenKey']
                    else:
                        print('Binance get listenKey error')
                    # keep listenkey alive every 30min
                    time.sleep(1800)
            except Exception as e:
                print(e)
        Thread(target=sign).start()

    def _connect(self, private=False):
        ws = None
        self._sign_message()
        while True:
            try:
                time.sleep(2)
                if private:
                    urlbase = f'{self.urlbase}?streams={self.listenKey}'
                    print('Binance start to connect ' + urlbase)
                    ws = websocket.create_connection(urlbase)
                else:
                    print('Binance start to connect ' + self.urlbase)
                    ws = websocket.create_connection(self.urlbase)
                break
            except Exception as e:
                print(f'Binance connect error {e}')
                continue
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
            print(e)

    def _sub(self, channel):
        try:
            params = {
                'method': 'SUBSCRIBE',
                'params': [channel],
                'id': self.SUB_ID
            }
            self.ws.send(json.dumps(params))
        except Exception as e:
            print(e)

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
            # 从本地data中找到到对应的订阅频道
            for key, value in self.data.items():
                if ''.join(key.split('_')) == ticker:
                    if len(value['kline']) > limit:
                        value['kline'].insert(0, kline)
                        value['kline'].pop()
                    else:
                        value['kline'].insert(0, kline)
                    break
        except Exception as e:
            print(f'Binance get kline error: {e}')

    def _get_trade(self, params: dict):
        try:
            ticker = params['stream'].split('@')[0].upper()  # ticker
            params = params['data']                          # data
            trade = {
                'count': float(params['q']),
                'order_time': round(params['E'] / 1000),
                'price': float(params['p']),
                'amount': float(params['q']) * float(params['p']),
                'type': 'sell' if params['m'] else 'buy'
            }
            for key, value in self.data.items():
                # standard for Bitmart symbol
                if ''.join(key.split('_')) == ticker:
                    value['trade'] = trade
                    value['price'] = trade['price']
        except Exception as e:
            print(f'Binance get trade error: {e}')

    def _get_orderbook(self, params: dict):
        try:
            ticker = params['stream'].split('@')[0].upper()
            params = params['data']
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
            for key, value in self.data.items():
                if ''.join(key.split('_')) == ticker:
                    value['orderbook'] = orderbook
        except Exception as e:
            print(f'Binance get orderbook error: {e}')

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
                # { key: { order: [detail1, detail2] } }
                for key, value in self.data.items():
                    if ''.join(key.split('_')) == order['symbol']:
                        order['symbol'] = key
                        index, isExist = 0, False
                        for item in value['order']:
                            # update order which exists in data
                            if item['create_time'] == order['create_time']:
                                value['order'][index] = order
                                isExist = True
                                break
                            index = index + 1
                        if not isExist:
                            if len(value['order']) > limit:
                                value['order'].pop(-1)
                            value['order'].insert(0, order)
        except Exception as e:
            print(f'Binance get order error: {e}')

    def _get_wallet_balance(self, params: dict):
        try:
            for row in params['B']:
                if row['a'] in self.data['wallet']:
                    self.data['wallet']['a'].update({
                        'balance': row['f'],
                        'frozen': row['l']
                    })
        except Exception as e:
            print(f'Binance get wallet error: {e}')

    # main function
    def on_message(self):
        def _message():
            try:
                while True:
                    recv = json.loads(self.ws.recv())
                    if 'stream' in recv:
                        # stream data
                        stream = '@'.join(recv['stream'].split('@')[1:])
                        switch = {
                            'trade': self._get_trade,
                            'kline_1m': self._get_kline,
                            'depth20@100ms': self._get_orderbook,
                        }
                        switch.get(stream, lambda recv: print(recv))(recv)
                    elif recv['id'] == self.SUB_ID:
                        recv = {
                            'code': 200,
                            'id': self.SUB_ID,
                            'data': 'ok',
                            'msg': 'Binance sub completely!'
                        }
                        print(recv)
                    elif recv['id'] == self.STOP_ID:
                        recv = {
                            'code': 200,
                            'id': self.STOP_ID,
                            'data': 'ok',
                            'msg': 'Binance stop sub completely!'
                        }
                        print(recv)
                    else:
                        raise Exception(f'STREAM DATA: {recv}')
            except websocket.WebSocketException as e:
                print(f'Binance Sub error {e} : try to connect again')
                self.ws = self._connect()
                self._sub(','.join(self.channel))
            except Exception as e:
                print(f'Binance Sub error {e}: connection end')
                self.ws.close()

        def _auth_message():
            try:
                while True:
                    recv = json.loads(self.wss.recv())
                    # print(recv)
                    if recv['e'] == 'outboundAccountPosition':
                        self._get_wallet_balance(recv)
                    elif recv['e'] == 'balanceUpdate':
                        print(recv)
                    elif recv['e'] == 'executionReport':
                        self._get_order(recv)
                    else:
                        print(recv)
            except websocket.WebSocketException as e:
                print(f'Binance Sub account error {e} : try to connect again')
                self._connect(private=True)
            except Exception as e:
                print(f'Binance Sub account error {e}: connection end')
                self.wss.close()
        Thread(target=_message).start()
        Thread(target=_auth_message).start()

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


if __name__ == '__main__':
    bw = BinanceWs('wss://stream.binance.com:9443/stream', 'peHvRKu7QGVZIezAlZfIAhmK5zPxa5ptLo6kkMOLGeJpD1UJhpufUVY6WvYqrDrh')
    # bw.sub_kline('BTC_USDT')
    # bw.sub_kline('ETH_BTC')
    bw.sub_price('BTC_USDT')
    # bw.sub_price('ETH_BTC')
    # bw.sub_orderbook('BTC_USDT')
    # bw.sub_orderbook('ETH_BTC')
    # bw.sub_trade('ETH_BTC')
    # bw.sub_trade('BTC_USDT')
    # bw.sub_order('BTC_USDT')
    # bw.sub_wallet_balance('BTC_USDT')

    while True:
        for i in range(20):
            time.sleep(2)
            print(bw.data['BTC_USDT']['price'])
            # if i == 6:
            #     bw.sub_orderbook('BTC_USDT')
            # if i == 16:
            #     bw.stop_orderbook('BTC_USDT')



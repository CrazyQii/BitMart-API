#!/usr/bin/python3
from threading import Thread, enumerate
from collections import defaultdict
from urllib import parse
from datetime import datetime
import websocket
import json
import time
import gzip
import hashlib
import hmac
import base64
import operator


class HuobiWs(Thread):
    def __init__(self, urlbase=None, api_key=None, api_secret=None, passphrase=None):
        super().__init__()
        if urlbase is None:
            self.urlbase = 'wss://api.huobi.pro/ws'
        else:
            self.urlbase = urlbase
        if api_key is None or api_secret is None:
            self.api_key = '4b145d1f-e62125b7-b23d557c-mk0lklo0de'
            self.api_secret = '95f79be7-490da711-a98b8019-5cd45'
        else:
            self.api_key = api_key
            self.api_secret = api_secret
        self._init_container()

    def _init_container(self):
        self.urlbaseV2 = self.urlbase + '/v2'
        self.channel = []
        self.data = defaultdict(dict)
        self.SUB_ID = 0                 # start to subscribe id
        self.STOP_ID = 1                # stop subscribing id
        self.ws = self._connect(private=False)  # create connection
        self.wss = self._connect(private=True)
        self.on_message()               # start receive data

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _channel_convert(self, channel: str):
        return '.'.join(channel.split('.')[2:])

    def _ts_to_uts(self):
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def _inflate(self, data):
        strdata = gzip.decompress(data).decode('utf-8')
        return json.loads(strdata)

    def _sign_message(self, params):
        try:
            sort = sorted(params.items(), key=operator.itemgetter(0))
            string = parse.urlencode(sort)
            host = parse.urlparse(self.urlbaseV2).hostname
            path = parse.urlparse(self.urlbaseV2).path
            msg = f'GET\n{host}\n{path}\n{string}'
            digest = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'),
                              digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(digest).decode()
            return sign
        except Exception as e:
            print(e)

    def _connect(self, private: bool):
        ws = None
        times = 0
        while True:
            try:
                if private:
                    urlbase = self.urlbase + '/v2'
                    print('Huobi start to connect ' + urlbase)
                    ws = websocket.create_connection(urlbase)
                    params = dict()
                    params['accessKey'] = self.api_key
                    params['signatureMethod'] = 'HmacSHA256'
                    params['signatureVersion'] = '2.1'
                    params['timestamp'] = self._ts_to_uts()
                    params['signature'] = self._sign_message(params)
                    params['authType'] = 'api'
                    data = {
                        'action': 'req',
                        'ch': 'auth',
                        'params': params
                    }
                    ws.send(json.dumps(data))
                else:
                    print('Huobi start to connect ' + self.urlbase)
                    ws = websocket.create_connection(self.urlbase)
            except Exception as e:
                print(f'Huobi connect error {e}')
                times = times + 1
                time.sleep(3)
                if times >= 5:
                    print(f'Huobi has connected {times} times, and connection end!!!')
                    break
            else:
                break
        return ws

    def _stop(self, channel):
        try:
            params = {
                'unsub': channel,
                'id': self.STOP_ID
            }
            self.ws.send(json.dumps(params))
        except Exception as e:
            print(e)

    def _sub(self, channel, private=False):
        try:
            if private:
                params = {
                    'action': 'sub',
                    'ch': channel
                }
                time.sleep(2)
                self.wss.send(json.dumps(params))
            else:
                params = {
                    'sub': channel,
                    'id': self.SUB_ID
                }
                self.ws.send(json.dumps(params))
        except Exception as e:
            print(e)

    def _get_kline(self, params: dict, limit=500):
        try:
            ticker = params['ch'].split('.')[1].upper()  # ticker
            params = params['tick']
            kline = {
                'timestamp': params['id'],
                'volume': float(params['amount']),
                'open': float(params['open']),
                'last_price': float(params['close']),
                'low': float(params['low']),
                'high': float(params['high'])
            }
            for key, value in self.data.items():
                if ''.join(key.split('_')) == ticker:
                    if len(value['kline']) > limit:
                        value['kline'].pop()
                    value['kline'].insert(0, kline)
                    break
        except Exception as e:
            print(f'Huobi get kline error: {e}')

    def _get_trade(self, params: dict):
        try:
            ticker = params['ch'].split('.')[1].upper()
            params = params['tick']['data'][0]  # data
            trade = {
                'count': float(params['amount']),
                'order_time': round(params['ts'] / 1000),
                'price': float(params['price']),
                'amount': float(params['amount']) * float(params['price']),
                'type': params['direction']
            }
            for key, value in self.data.items():
                # standard for Bitmart symbol
                if ''.join(key.split('_')) == ticker:
                    value['trade'] = trade
        except Exception as e:
            print(f'Huobi get trade error: {e}')

    def _get_price(self, params: dict):
        try:
            ticker = params['ch'].split('.')[1].upper()
            price = {
                'price': params['tick']['close'],
                'timestamp': round(params['ts'] / 1000)
            }  # data
            for key, value in self.data.items():
                # standard for Bitmart symbol
                if ''.join(key.split('_')) == ticker:
                    value['price'] = price
                    break
        except Exception as e:
            print(f'Huobi get price error: {e}')

    def _get_orderbook(self, params: dict):
        try:
            ticker = params['ch'].split('.')[1].upper()
            orderbook = {'buys': [], 'sells': []}
            params = params['tick']
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
                    break
        except Exception as e:
            print(f'Huobi get orderbook error: {e}')

    def _get_order(self, params: dict, status=None, limit=200):
        if status is None:
            status = ['submitted', 'partial-filled', 'partial-canceled']
        try:
            params = params['data']
            if len(params) > 0 and params['orderStatus'] in status:
                order = {
                    'order_id': params['orderId'],
                    'symbol': params['symbol'],
                    'price': float(params['orderPrice']),
                    'amount': float(params['orderSize']),
                    'side': params['type'].split('-')[0],
                    'price_avg': float(float(params['orderPrice']) / float(params['orderSize'])),
                    'filled_amount': float(params['execAmt']),
                    'status': params['orderStatus'],
                    'create_time': round(params['lastActTime'] / 1000),
                }
                for key, value in self.data.items():
                    if ''.join(key.split('_')) == order['symbol'].upper():
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
            print(f'Huobi get order error: {e}')

    def _get_wallet_balance(self, params: dict):
        try:
            params = params['data']
            if len(params) > 0:
                ticker = params['currency'].upper()
                if ticker in self.data['wallet']:
                    self.data['wallet'][ticker].update({
                        'balance': params['balance'],
                        'frozen': None
                    })
        except Exception as e:
            print(f'Huobi get wallet balance error: {e}')

    def on_message(self):
        def _message():
            try:
                if self.ws is None:
                    print('Huobi public does not connected, and connection closed!')
                else:
                    while True:
                        recv = self._inflate(self.ws.recv())
                        if 'ch' in recv:
                            stream = self._channel_convert(recv['ch'])
                            switch = {
                                'trade.detail': self._get_trade,
                                'kline.1min': self._get_kline,
                                'detail': self._get_price,
                                'mbp.refresh.20': self._get_orderbook
                            }
                            switch.get(stream, lambda r: print(r))(recv)
                        elif 'ping' in recv:
                            self.ws.send(json.dumps({'pong': recv['ping']}))
                        elif 'status' in recv and recv['status'] == 'ok':
                            if 'subbed' in recv:
                                self.channel.append(recv['subbed'])
                                recv = {
                                    'code': 200,
                                    'id': self.SUB_ID,
                                    'data': recv['status'],
                                    'msg': 'Huobi sub completely!'
                                }
                                print(recv)
                            if 'unsubbed' in recv:
                                self.channel.remove(recv['unsubbed'])
                                recv = {
                                    'code': 200,
                                    'id': self.STOP_ID,
                                    'data': recv['status'],
                                    'msg': 'Huobi unsub completely!'
                                }
                                print(recv)
                        else:
                            print(recv)
                            break
            except Exception as e:
                print(f'Huobi Sub public error {e} : try to connect again')
                self.ws = self._connect(private=False)
                self._sub(','.join(self.channel))
                _message()

        def _auth_message():
            try:
                if self.wss is None:
                    print('Okex auth does not connected, and connection closed!')
                while True:
                    recv = json.loads(self.wss.recv())
                    if recv['action'] == 'req' and recv['code'] == 200:
                        print({
                            'code': recv['code'],
                            'id': 0,
                            'data': 'ok',
                            'msg': 'Huobi login successfully'
                        })
                    elif recv['action'] == 'sub' and recv['code'] == 200:
                        stream = recv['ch'].split('#')[0]
                        switch = {
                            'accounts.update': self._get_wallet_balance,
                            'orders': self._get_order,
                        }
                        switch.get(stream, lambda r: print(r))(recv)
                    elif recv['action'] == 'ping':
                        self.wss.send(json.dumps({
                            'action': 'pong',
                            'data': {'ts': recv['data']['ts']}
                        }))
                    else:
                        print({
                            'code': recv['code'],
                            'id': 0,
                            'data': recv['ch'],
                            'msg': f'Huobi {recv["message"]}'
                        })
            except Exception as e:
                print(f'Huobi Sub auth error {e} : try to connect again')
                self.wss = self._connect(True)
                self._sub(','.join(self.channel))
                _auth_message()

        Thread(target=_message).start()
        # Thread(target=_auth_message).start()

    # subscribe
    def sub_price(self, symbol: str):
        self.data[symbol]['price'] = None
        self._sub(f'market.{self._symbol_convert(symbol)}.detail')

    def sub_kline(self, symbol: str):
        self.data[symbol]['kline'] = []
        self._sub(f'market.{self._symbol_convert(symbol)}.kline.1min')

    def sub_orderbook(self, symbol: str):
        self.data[symbol]['orderbook'] = None
        self._sub(f'market.{self._symbol_convert(symbol)}.mbp.refresh.20')

    def sub_trade(self, symbol: str):
        self.data[symbol]['trade'] = None
        self._sub(f'market.{self._symbol_convert(symbol)}.trade.detail')

    # subscribe account
    def sub_wallet_balance(self, symbol: str):
        self.data['wallet'] = {
            symbol.split('_')[0]: {'balance': None, 'frozen': None},
            symbol.split('_')[1]: {'balance': None, 'frozen': None},
        }
        self._sub('accounts.update#1', private=True)

    def sub_order(self, symbol: str):
        self.data[symbol]['order'] = []
        self._sub(f'orders#{self._symbol_convert(symbol)}', private=True)

    # stop subscribe
    def stop_kline(self, symbol: str):
        self._stop(f'market.{self._symbol_convert(symbol)}.kline.1min')

    def stop_price(self, symbol: str):
        self._stop(f'market.{self._symbol_convert(symbol)}.detail')

    def stop_orderbook(self, symbol: str):
        self._stop(f'market.{self._symbol_convert(symbol)}.mbp.refresh.20')

    def stop_trade(self, symbol: str):
        self._stop(f'market.{self._symbol_convert(symbol)}.trade.detail')


# huobi = HuobiWs()


if __name__ == '__main__':
    b = HuobiWs()
    # b.sub_price('BTC_USDT')
    # b.sub_trade('BTC_USDT')
    # b.sub_kline('BTC_USDT')
    b.sub_orderbook('BTC_USDT')
    while True:
        time.sleep(1)
        # print(enumerate())
        print(b.data['BTC_USDT'])
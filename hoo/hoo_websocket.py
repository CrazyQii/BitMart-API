# -*- coding:utf-8 -*-
"""
Hoo websocket API
2020/10/10 hlq
"""

import websocket
import faker
import hashlib
import time
import hmac
import json
from threading import Thread

f = faker.Faker(locale='zh-CN')


class MyThread(Thread):
    """ rewrite Thread class """
    def __init__(self, target=None, args=None):
        """
        target: function name
        args: the results that need to be output
        """
        super(MyThread, self).__init__()
        self.func = target
        self.result = args

    def run(self):
        try:
            self.func()
            raise Exception('An error occured here, check MyThread')
        except Exception as e:
            print(e)
            return None

    def get_result(self):
        """ return function result """
        try:
            return self.result
        except Exception as e:
            print(e)
            return None


class HooWss(object):
    def __init__(self, urlbase, api_key, api_secret):
        self.urlbase = urlbase
        self.client_id = api_key
        self.client_key = api_secret
        self.data = []

    def _symbol_convert(self, symbol: str):
        return '-'.join(symbol.split('_'))

    def _sign_message(self):
        try:
            """ Authentication """
            ts = int(time.time())
            nonce = f.md5()
            message = f'client_id={self.client_id}&nonce={nonce}&ts={ts}'
            sign = hmac.new(bytes(self.client_key, encoding='utf-8'), bytes(message, encoding='utf-8'),
                            digestmod=hashlib.sha256)
            sign_message = {
                'op': 'apilogin',
                'sign': sign.hexdigest(),
                'client_id': self.client_id,
                'nonce': nonce,
                'ts': ts
            }
            return sign_message
        except Exception as e:
            print(e)

    def _connect(self, fun: str):
        """ connect websocket """
        try:
            print(f'start to connect {self.urlbase} - {fun}')
            ws = websocket.create_connection(self.urlbase)

            # login API
            obj = self._sign_message()
            ws.send(json.dumps(obj))

            # verify if login successfully
            recv = json.loads(ws.recv())
            if recv['code'] == 0:
                return ws
        except Exception as e:
            print(e)

    def sub_hb(self):
        def _hb():
            ws = self._connect('sub_hb')
            try:
                while True:
                    data = {'op': 'sub', 'topic': 'hb'}
                    ws.send(json.dumps(data))
                    time.sleep(15)

            except websocket.WebSocketException as e:
                print(e)
                ws.close()
        return MyThread(target=_hb).start()

    def sub_kline(self, symbol: str, time_period=60):
        def _kline():
            ws = self._connect('sub_kline')
            try:
                if time_period % 60 != 0:
                    raise Exception('time period must be integer multiple of 60')
                sub = f'kline:{int(time_period / 60)}Min:{self._symbol_convert(symbol)}'
                data = {'op': 'sub', 'topic': sub}

                # send sub request
                ws.send(json.dumps(data))
                recv = json.loads(ws.recv())

                # receive resp
                if recv['code'] != 0:
                    return None

                while True:
                    # receive info
                    recv = json.loads(ws.recv())['ticks'][0]
                    result = {
                        'timestamp': recv['timestamp'],
                        'volume': recv['volume'],
                        'open_price': recv['open'],
                        'current_price': recv['close'],
                        'lowest_price': recv['low'],
                        'highest_price': recv['high']
                    }
                    self.data.append(result)
            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            except websocket.WebSocketException as e:
                print(e)
            finally:
                # close the connection
                ws.close()

        # send heart
        self.sub_hb()
        # return a new thread and start it
        return MyThread(target=_kline).start()

    def sub_price(self, symbol: str):
        def _trade():
            ws = self._connect('sub_price')
            try:
                data = {'op': 'sub', 'topic': f'trade:{self._symbol_convert(symbol)}'}

                ws.send(json.dumps(data))
                recv = json.loads(ws.recv())

                if recv['code'] != 0:
                    return None

                while True:
                    trade = json.loads(ws.recv())
                    self.data.append(float(trade['price']))
            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            finally:
                ws.close()

        # send heart
        self.sub_hb()
        return MyThread(target=_trade).start()

    def sub_orderbook(self, symbol: str):
        def _orderbook():
            ws = self._connect('sub_orderbook')
            try:
                data = {'op': 'sub', 'topic': f'depth:0:{self._symbol_convert(symbol)}'}

                ws.send(json.dumps(data))
                recv = json.loads(ws.recv())

                if recv['code'] != 0:
                    return None

                while True:
                    orderbook = json.loads(ws.recv())
                    result = {
                        'bids': [],
                        'asks': []
                    }
                    for item in orderbook['bids']:
                        result['bids'].append([float(item['price']), float(item['quantity'])])
                    for item in orderbook['asks']:
                        result['asks'].append([float(item['price']), float(item['quantity'])])
                    self.data.append(result)
            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            finally:
                ws.close()

        # send heart
        self.sub_hb()
        return MyThread(target=_orderbook).start()

    def result(self):
        """ get result"""
        return MyThread(args=self.data).get_result()


if __name__ == "__main__":

    hoo = HooWss('wss://api.hoolgd.com/ws', "iJsVEJDESyTXdm8hRBuf79fANdwNB5",
                                  "J7EqDCc6FaKA8n5nCy8WJ1uoM4HSZeg2k43mepX5TNjz1qLHUs")
    # hoo.sub_hb()

    hoo.sub_kline('BTC_USDT')
    # hoo.sub_price('BTC_USDT')
    # hoo.sub_orderbook('BTC_USDT')

    while True:
        time.sleep(10)
        print(hoo.result())

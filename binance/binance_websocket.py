"""
binance webscoket API
2020/10/12 hlq
"""

from threading import Thread
import websocket
import json
import time


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
        try:
            return self.result
        except Exception as e:
            print(e)
            return None


class BinWss(object):
    def __init__(self, urlbase, api_key=None, api_secret=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.data = []

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _connect(self, path):
        ws = None
        try:
            url = self.urlbase + path
            print('start to connect ' + url)
            ws = websocket.create_connection(url)
        except websocket.WebSocketException as e:
            print(e)
        finally:
            return ws

    def _send_pong(self, ws):
        """ keep connect """
        def _pong():
            try:
                while True:
                    ws.send(json.dumps({'pong': '1'}))
                    print('sfd')
                    time.sleep(60)
            except websocket.WebSocketException as e:
                print(e)
                ws.close()
        MyThread(target=_pong).start()

    def sub_kline(self, symbol: str, interval=60):
        def _kline():
            if interval % 3 != 0 or interval % 5 != 0:
                raise Exception('time period must be integer multiple of 3 or 5')
            elif interval < 60:
                raise Exception('interval must larger than 60')
            else:
                interval_time = int(interval / 60)

            path = f'/ws/{self._symbol_convert(symbol)}@kline_{interval_time}m'
            ws = self._connect(path)

            try:
                while True:
                    recv = json.loads(ws.recv())
                    result = {
                        'timestamp': recv['E'],
                        'volume': recv['k']['v'],
                        'open_price': recv['k']['o'],
                        'current_price': recv['k']['c'],
                        'lowest_price': recv['k']['l'],
                        'highest_price': recv['k']['h']
                    }
                    self.data.append(result)

            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            except websocket.WebSocketException as e:
                print(e)
            finally:
                if ws is None:
                    print('connect fail')
                else:
                    ws.close()
        MyThread(target=_kline).start()

    def sub_price(self, symbol: str):
        def _trade():
            path = f'/ws/{self._symbol_convert(symbol)}@trade'

            ws = self._connect(path)
            try:
                while True:
                    trade = json.loads(ws.recv())
                    self.data.append(float(trade['p']))
            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            finally:
                ws.close()
        return MyThread(target=_trade).start()

    def sub_orderbook(self, symbol: str, levels=5):
        def _orderbook():
            path = f'/ws/{self._symbol_convert(symbol)}@depth{levels}'
            ws = self._connect(path)
            try:
                while True:
                    orderbook = json.loads(ws.recv())
                    result = {
                        'bids': [],
                        'asks': []
                    }
                    for item in orderbook['bids']:
                        result['bids'].append([float(item[0]), float(item[1])])
                    for item in orderbook['asks']:
                        result['asks'].append([float(item[0]), float(item[1])])

                    self.data = result
            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            finally:
                ws.close()
        return MyThread(target=_orderbook).start()

    def result(self):
        """ get result"""
        return MyThread(args=self.data).get_result()


if __name__ == '__main__':
    bw = BinWss('wss://stream.binance.com:9443')
    # bw.sub_kline('BTC_USDT')
    # bw.sub_price('BTC_USDT')
    bw.sub_orderbook('BTC_USDT')

    while True:
        while True:
            print(bw.result())
            time.sleep(10)


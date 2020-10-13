"""
okex websocket API
2020/10/12 hlq
"""

from threading import Thread
import websocket
import hashlib
import hmac
import time
import base64
import json
import zlib
import requests
import dateutil.parser as dp


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
            raise Exception('MyThread stop')
        except Exception as e:
            print(e)
            return None

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print(e)
            return None


class OkexWss(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.data = []

    def _symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))

    def _server_timestamp(self):
        try:
            url = "https://www.okex.com/api/general/v3/time"
            response = requests.get(url)
            if response.status_code == 200:
                server_time = response.json()['iso']
                timestamp = dp.parse(server_time).timestamp()
                return timestamp
            else:
                return ""
        except Exception as e:
            print(e)

    def _sign_message(self):
        try:
            message = f'{self._server_timestamp()}GET/users/self/verify'

            mac = hmac.new(bytes(self.api_secret, encoding='utf8'), bytes(message, encoding='utf-8'),
                           digestmod=hashlib.sha256)
            d = mac.digest()
            sign = base64.b64encode(d)

            login_param = {"op": "login", "args": [self.api_key, self.passphrase, self._server_timestamp(),
                                                   sign.decode("utf-8")]}
            return json.dumps(login_param)
        except Exception as e:
            print(e)

    def _inflate(self, data):
        try:
            decompress = zlib.decompressobj(
                -zlib.MAX_WBITS  # see above
            )
            inflated = decompress.decompress(data)
            inflated += decompress.flush()
            return inflated
        except Exception as e:
            print(e)

    def _connect(self):
        """ connect websocket """
        ws = None
        try:
            print(f'start to connect {self.urlbase}')
            ws = websocket.create_connection(self.urlbase)
        except Exception as e:
            print(e)
        finally:
            return ws

    def sub_kline(self, symbol: str, time_period=60):
        def _kline():
            ws = self._connect()
            try:
                params = {'op': 'subscribe', 'args': [f'spot/candle{time_period}s:{self._symbol_convert(symbol)}']}
                ws.send(json.dumps(params))

                # parse recv
                recv = eval(self._inflate(ws.recv()).decode('utf-8'))

                if recv['event'] != 'subscribe':
                    print(' subscribe fail! ')
                    return None

                while True:
                    recv = eval(self._inflate(ws.recv()).decode('utf-8'))
                    res = recv['data'][0]['candle']
                    result = {
                        'timestamp': res[0],
                        'volume': res[5],
                        'open_price': res[1],
                        'current_price': res[4],
                        'lowest_price': res[3],
                        'highest_price': res[2]
                    }
                    self.data.append(result)

            except websocket.WebSocketException as e:
                print(e)
            finally:
                ws.close()
        MyThread(target=_kline).start()

    def sub_price(self, symbol: str):
        def _trade():
            ws = self._connect()
            try:
                params = {'op': 'subscribe', 'args': [f'spot/ticker:{self._symbol_convert(symbol)}']}
                ws.send(json.dumps(params))

                # parse recv
                recv = eval(self._inflate(ws.recv()).decode('utf-8'))

                if recv['event'] != 'subscribe':
                    print(' subscribe fail! ')
                    return None

                while True:
                    trade = eval(self._inflate(ws.recv()).decode('utf-8'))
                    self.data.append(float(trade['data'][0]['last']))
            except websocket.WebSocketConnectionClosedException as e:
                print(e)
            finally:
                ws.close()

        return MyThread(target=_trade).start()

    def sub_orderbook(self, symbol: str, depth=5):
        def _orderbook():
            ws = self._connect()
            try:
                params = {'op': 'subscribe', 'args': [f'spot/depth{depth}:{self._symbol_convert(symbol)}']}
                ws.send(json.dumps(params))

                # parse recv
                recv = eval(self._inflate(ws.recv()).decode('utf-8'))

                if recv['event'] != 'subscribe':
                    print(' subscribe fail! ')
                    return None

                while True:
                    orderbook = eval(self._inflate(ws.recv()).decode('utf-8'))
                    orderbook = orderbook['data'][0]
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
    import asyncio
    okws = OkexWss('wss://real.okex.com:8443/ws/v3',"dda0063c-70fc-42b1-8390-281e77b532a5", "A06AFB73716F15DC1805D183BCE07BED", "okexpassphrase")

    # okws.sub_kline('BTC_USDT')
    # okws.sub_price('BTC_USDT')
    # okws.sub_orderbook('BTC_USDT')

    while True:
        time.sleep(10)
        print(okws.result())

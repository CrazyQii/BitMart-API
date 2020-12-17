from threading import Thread
from datetime import datetime
from collections import defaultdict
import websocket
import hashlib
import hmac
import time
import base64
import json
import zlib


class OkexWss(Thread):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        super().__init__()
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self._init_container()

    def _init_container(self):
        self.data = defaultdict(dict)
        self.channel = []
        self.start_time = None                          # keep alive
        self.header_ts = str(round(time.time(), 3))     # sign timestamp
        self.sign = self._sign_message()                # sign
        self.ws = self._connect()
        self.on_message()

    def _symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _inflate(self, data):
        try:
            decompress = zlib.decompressobj(
                -zlib.MAX_WBITS  # see above
            )
            inflated = decompress.decompress(data)
            inflated += decompress.flush()
            return inflated.decode('utf-8')
        except Exception as e:
            print(e)

    def _sign_message(self):
        try:
            message = f'{self.header_ts}GET/users/self/verify'
            digest = hmac.new(bytes(self.api_secret, encoding='utf8'), bytes(message, encoding='utf-8'),
                              digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(digest).decode('utf-8')
            return sign
        except Exception as e:
            print(e)

    def _connect(self):
        ws = None
        while True:
            try:
                time.sleep(2)
                print('Okex start to connect ' + self.urlbase)
                headers = {
                    'OK-ACCESS-KEY': self.api_key,
                    'OK-ACCESS-SIGN': self.sign,
                    'OK-ACCESS-TIMESTAMP': self.header_ts,
                    'OK-ACCESS-PASSPHRASE': self.passphrase,
                    'Content-Type': 'application/json'
                }
                ws = websocket.create_connection(self.urlbase, header=headers)
                break
            except Exception as e:
                print(f'Okex connect error {e}')
                continue
        return ws

    def _stop(self, channel):
        try:
            params = {
                'op': 'unsubscribe',
                'args': [channel]
            }
            self.ws.send(json.dumps(params))
        except Exception as e:
            print(e)

    def _sub(self, channel, private=False):
        try:
            if private:
                params = {
                    'op': 'login',
                    'args': [self.api_key, self.passphrase, self.header_ts, self.sign]
                }
            else:
                params = {
                    'op': 'subscribe',
                    'args': [channel]
                }
            self.ws.send(json.dumps(params))
        except Exception as e:
            print(e)

    def _get_kline(self, params: dict, limit=500):
        try:
            ticker = '_'.join(params['data'][0]['instrument_id'].split('-'))
            params = params['data'][0]['candle']
            kline = {
                'timestamp': self._utc_to_ts(params[0]),
                'volume': float(params[5]),
                'open': float(params[1]),
                'last_price': float(params[4]),
                'low': float(params[3]),
                'high': float(params[2])
            }
            if len(self.data[ticker]['kline']) > limit:
                self.data[ticker]['kline'].insert(0, kline)
                self.data[ticker]['kline'].pop()
            else:
                self.data[ticker]['kline'].insert(0, kline)
        except Exception as e:
            print(f'Okex get kline error: {e}')

    def _get_trade(self, params: dict):
        try:
            ticker = '_'.join(params['data'][0]['instrument_id'].split('-'))
            params = params['data'][0]
            trade = {
                'count': float(params['size']),
                'order_time': self._utc_to_ts(params['timestamp']),
                'price': float(params['price']),
                'amount': float(params['size']) * float(params['price']),
                'type': params['side']
            }
            self.data[ticker]['trade'] = trade
        except Exception as e:
            print(f'Okex get trade error: {e}')

    def _get_price(self, params: dict):
        try:
            ticker = '_'.join(params['data'][0]['instrument_id'].split('-'))
            params = params['data'][0]
            self.data[ticker]['price'] = params['last']
        except Exception as e:
            print(f'Okex get price error: {e}')

    def _get_orderbook(self, params: dict):
        try:
            ticker = '_'.join(params['data'][0]['instrument_id'].split('-'))
            if params['action'] == 'partial':
                # partial part
                params = params['data'][0]
                orderbook = {'buys': [], 'sells': []}
                total_amount_buys = 0
                total_amount_sells = 0
                for item in params['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
                for item in params['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
                self.data[ticker]['orderbook'] = orderbook
            else:
                # update part
                params = params['data'][0]
                for ask_new in params['asks']:
                    index, is_new = 0, False
                    for ask_old in self.data[ticker]['orderbook']['sells']:
                        if ask_old['price'] == ask_new[0]:
                            if ask_new[1] == 0:
                                self.data[ticker]['orderbook']['sells'].pop(index)
                            else:
                                self.data[ticker]['orderbook']['sells'][index] = {
                                    'amount': ask_new(ask_new[1]),
                                    'total': None,  # 无法计算
                                    'price': float(ask_new[0]),
                                    'count': ask_new[0]
                                }
                        index = index + 1
                    if is_new:
                        self.data[ticker]['orderbook']['ask'].append({
                            'amount': float(ask_new[1]),
                            'total': None,  # 无法计算
                            'price': float(ask_new[0]),
                            'count': ask_new[2]
                        })
                for buy_new in params['bids']:
                    index, is_new = 0, True
                    for ask_old in self.data[ticker]['orderbook']['buys']:
                        if ask_old['price'] == buy_new[0]:
                            is_new = False
                            if buy_new[1] == 0:
                                self.data[ticker]['orderbook']['buys'].pop(index)
                            else:
                                self.data[ticker]['orderbook']['buys'][index] = {
                                    'amount': float(buy_new[1]),
                                    'total': None,  # 无法计算
                                    'price': float(buy_new[0]),
                                    'count': buy_new[2]
                                }
                        index = index + 1
                    if is_new:
                        self.data[ticker]['orderbook']['buys'].append({
                            'amount': float(buy_new[1]),
                            'total': None,  # 无法计算
                            'price': float(buy_new[0]),
                            'count': buy_new[2]
                        })
        except Exception as e:
            print(f'Okex get orderbook error: {e}')

    def _get_order(self, params: dict, status=None, limit=200):
        if status is None:
            status = ['0', '1', '3']
        try:
            ticker = '_'.join(params['data'][0]['instrument_id'].split('-'))
            params = params['data'][0]
            if params['state'] in status:
                order = {
                    'order_id': params['order_id'],
                    'symbol': ticker,
                    'price': float(params['price']),
                    'amount': float(params['size']),
                    'side': params['side'],
                    'price_avg': float(float(params['price']) / float(params['size'])),
                    'filled_amount': float(params['filled_size']),
                    'status': params['state'],
                    'create_time': self._utc_to_ts(params['timestamp']),
                }
                index, isExist = 0, False
                for item in self.data[ticker]['order']:
                    # update order which exists in data
                    if item['create_time'] == order['create_time']:
                        self.data[ticker]['order'][index] = order
                        isExist = True
                        break
                    index = index + 1
                if not isExist:
                    if len(self.data[ticker]['order']) > limit:
                        self.data[ticker]['order'].pop(-1)
                    self.data[ticker]['order'].insert(0, order)
        except Exception as e:
            print(f'Okex get order error: {e}')

    def _get_wallet_balance(self, params: dict):
        try:
            ticker = params['data']['currency']
            balance = params['data']['available']
            frozen = params['data']['hold']
            self.data['wallet'].update({
                ticker: {
                    'balance': balance,
                    'frozen': frozen
                }
            })
        except Exception as e:
            print(f'Okex get wallet balance error: {e}')

    def _ping(self):
        while True:
            if time.time() - self.start_time > 20:
                self.ws.send('ping')
            time.sleep(1)

    def on_message(self):
        def _message():
            try:
                while True:
                    # record interval time
                    self.start_time = time.time()
                    # start to receive data
                    recv = self._inflate(self.ws.recv())
                    if recv == 'pong':
                        print('pong')
                        continue
                    else:
                        if recv is None:
                            raise Exception('Receive is None')
                        else:
                            recv = json.loads(recv)
                    if 'table' in recv:
                        switch = {
                            'spot/ticker': self._get_price,
                            'spot/trade': self._get_trade,
                            'spot/candle60s': self._get_kline,
                            'spot/depth': self._get_orderbook,
                            'spot/account': self._get_wallet_balance,
                            'spot/order': self._get_order
                        }
                        switch.get(recv['table'], lambda recv: print(recv))(recv)
                    elif 'event' in recv:
                        switch = {
                            'login': lambda recv: print({
                                'code': 200,
                                'id': 2,
                                'data': recv['success'],
                                'msg': 'Okex login completely!'
                            }),
                            'subscribe': lambda recv: print({
                                'code': 200,
                                'id': 0,
                                'data': 'ok',
                                'msg': f'Okex sub \'{recv["channel"]}\' completely!'
                            }),
                            'unsubscribe': lambda recv: print({
                                'code': 200,
                                'id': 1,
                                'data': 'ok',
                                'msg': f'Okex unsub \'{recv["channel"]}\' completely!'
                            })
                        }
                        switch.get(recv['event'], lambda recv: print(recv))(recv)
                    else:
                        raise Exception(f'STREAM DATA: {recv}')
            except websocket.WebSocketException as e:
                print(f'Okex Sub error {e} : try to connect again')
                self.ws = self._connect()
                self._sub(','.join(self.channel))
            except Exception as e:
                print(f'Okex Sub error {e}: connection end')
                self.ws.close()

        Thread(target=_message).start()
        time.sleep(1)
        Thread(target=self._ping).start()

    # subscribe
    def sub_kline(self, symbol: str):
        self.data[symbol]['kline'] = []
        self._sub(f'spot/candle60s:{self._symbol_convert(symbol)}')

    def sub_price(self, symbol: str):
        self.data[symbol]['price'] = None
        self._sub(f'spot/ticker:{self._symbol_convert(symbol)}')

    def sub_trade(self, symbol: str):
        self.data[symbol]['trade'] = None
        self._sub(f'spot/trade:{self._symbol_convert(symbol)}')

    def sub_orderbook(self, symbol: str):
        self.data[symbol]['orderbook'] = None
        self._sub(f'spot/depth:{self._symbol_convert(symbol)}')

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
        self._sub(None, private=True)
        time.sleep(1)
        self._sub(f'spot/account:{symbol.split("_")[0]}')
        time.sleep(2)
        self._sub(f'spot/account:{symbol.split("_")[1]}')

    def sub_order(self, symbol: str):
        self.data[symbol]['order'] = []
        self._sub(None, private=True)
        time.sleep(2)
        self._sub(f'spot/order:{self._symbol_convert(symbol)}')

    # stop subscribe
    def stop_kline(self, symbol: str):
        self._stop(f'spot/candle60s:{self._symbol_convert(symbol)}')

    def stop_price(self, symbol: str):
        self._stop(f'spot/ticker:{self._symbol_convert(symbol)}')

    def stop_trade(self, symbol: str):
        self._stop(f'spot/trade:{self._symbol_convert(symbol)}')

    def stop_orderbook(self, symbol: str):
        self._stop(f'spot/depth:{self._symbol_convert(symbol)}')


if __name__ == '__main__':
    okws = OkexWss('wss://real.okex.com:8443/ws/v3', 'dda0063c-70fc-42b1-8390-281e77b532a5', 'A06AFB73716F15DC1805D183BCE07BED', 'okexpassphrase')
    # okws.sub_kline('BTC_USDT')
    okws.sub_price('BTC_USDT')
    # okws.sub_orderbook('BTC_USDT')
    # okws.sub_trade('BTC_USDT')
    # okws.sub_trade('ETH_BTC')
    # okws.sub_wallet_balance('BTC_USDT')
    # okws.sub_order('BTC_USDT')

    while True:
        for i in range(10):
            time.sleep(2)
            print(okws.data['BTC_USDT']['price'])
    #         if i == 4:
    #             okws.stop_kline('BTC_USDT')
    #         if i == 8:
    #             okws.sub_kline('BTC_USDT')

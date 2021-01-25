#!/usr/bin/python3
# -*- coding: utf-8 -*-
from threading import Thread, enumerate
from collections import defaultdict
from urllib.parse import urlencode
import requests
import websocket
import json
import time
import operator
import hmac
import hashlib
import logging


class WootradeWs(Thread):
    def __init__(self, urlbase=None, api_key=None, api_secret=None, passphrase=None):
        super().__init__()
        if urlbase is None:
            self.urlbase = 'wss://api.woo.network/ws/'
        else:
            self.urlbase = urlbase
        if api_key is None or api_secret is None:
            self.api_key = 'AbmyVJGUpN064ks5ELjLfA=='
            self.api_secret = 'QHKRXHPAW1MC9YGZMAT8YDJG2HPR'
        else:
            self.api_key = api_key
            self.api_secret = api_secret
        self._init_container()

    def _init_container(self):
        self.rest_url = 'https://api.woo.network/v1/client/info'
        self.data = defaultdict(dict)
        self.application_id = self._get_account_id()
        if self.application_id is None:
            self.application_id = 'e1f40bde-0e4e-4c2c-b369-bd00e434b754'

    def _symbol_convert(self, symbol: str):
        return 'SPOT_' + symbol

    def _sign_message(self, ts, params=None):
        try:
            if params is not None:
                sort = sorted(params.items(), key=operator.itemgetter(0))
            else:
                sort = ''
            msg = urlencode(sort)
            msg += '|' + ts
            return hmac.new(self.api_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
        except Exception as e:
            logging.error(f'wootrade sign message error: {e}')

    def _get_account_id(self):
        try:
            ts = str(time.time() * 1000)
            sign = self._sign_message(ts)
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                       'x-api-key': self.api_key,
                       'x-api-signature': sign,
                       'x-api-timestamp': ts,
                       'cache-control': 'no-cache'}
            url = self.rest_url
            resp = requests.get(url, headers=headers).json()
            if resp['success']:
                return resp['application']['application_id']
            else:
                logging.error(f'Wootrade auth get account id error: {resp}')
        except Exception as e:
            logging.error(f'Wootrade auth get account id error: {e}')

    def _connect(self, symbol: str, private: bool, streams=None):
        if private:
            ws = None
            times = 0
            symbol = self._symbol_convert(symbol)
            sub_url = f'{self.urlbase}{self.application_id}/{symbol}'
            while True:
                try:
                    time.sleep(2)
                    logging.info(f'Wootrade start to connect auth {sub_url}')
                    ws = websocket.create_connection(sub_url)
                except Exception as e:
                    logging.error(f'Wootrade connect auth error {e}')
                    times = times + 1
                    if times >= 5:
                        logging.error(f'Wootrade has connected {times} times, and connection end!!!')
                        break
                else:
                    break
            return ws
        else:
            if streams is None:
                streams = ['ticker']
            ws = None
            times = 0
            sub_url = f'{self.urlbase}stream?streams={",".join(streams)}'
            while True:
                try:
                    time.sleep(2)
                    logging.info(f'Wootrade start to connect public {sub_url}')
                    ws = websocket.create_connection(sub_url)
                except Exception as e:
                    logging.error(f'Wootrade connect public error {e}')
                    times = times + 1
                    if times >= 5:
                        logging.error(f'Wootrade has connected {times} times, and connection end!!!')
                        break
                else:
                    break
            return ws

    def _get_price(self, symbol: str, params: dict):
        try:
            for ticker in params['data']:
                if self._symbol_convert(symbol) == ticker['symbol']:
                    self.data[symbol]['price'] = {
                        'price': ticker['c'],
                        'timestamp': round(params['timestamp'] / 1000)
                    }
        except Exception as e:
            logging.error(f'Wootrade get price error: {e}')

    def _get_orderbook(self, symbol: str, params: dict):
        try:
            orderbook = {'buys': [], 'sells': []}
            total_amount_buys = 0
            total_amount_sells = 0
            for item in params['data']['bids']:
                total_amount_buys += float(item['quantity'])
                orderbook['buys'].append({
                    'amount': float(item['quantity']),
                    'total': total_amount_buys,
                    'price': float(item['price']),
                    'count': 1
                })
            for item in params['data']['asks']:
                total_amount_sells += float(item['quantity'])
                orderbook['sells'].append({
                    'amount': float(item['quantity']),
                    'total': total_amount_sells,
                    'price': float(item['price']),
                    'count': 1
                })
            self.data[symbol].update({
                'orderbook': orderbook
            })
        except Exception as e:
            logging.error(f'Wootrade get orderbook error: {e}')

    def _get_trade(self, symbol: str, params: dict):
        try:
            trade = params['data']
            trade = {
                'amount': float(trade['quantity']) * float(trade['price']),
                'order_time': round(params['timestamp'] / 1000),
                'price': float(trade['price']),
                'count': float(trade['quantity']),
                'type': trade['side'].lower()
            }
            self.data[symbol].update({
                'trade': trade
            })
        except Exception as e:
            logging.error(f'Wootrade get trade error: {e}')

    def _get_order(self, symbol: str, params: dict, status=None, limit=200):
        try:
            if status is None:
                status = ['PARTIAL_FILLED']
            order = params['data']
            if 'order' not in self.data[symbol]:
                self.data[symbol]['order'] = []
            if order['status'] in status:
                order = {
                    'order_id': order['order_id'],
                    'symbol': symbol,
                    'side': order['side'].lower(),
                    'price': float(order['order_price']),
                    'amount': float(order['order_quantity']),
                    'price_avg': float(float(order['order_price']) / float(order['order_quantity'])),
                    'filled_amount': float(order['executed_quantity']),
                    'status': order['status'],
                    'create_time': round(params['timestamp'] / 1000)
                }
                index, isExist = 0, False
                for item in self.data[symbol]['order']:
                    # update order which exists in data
                    if item['create_time'] == order['create_time']:
                        self.data[symbol]['order'][index] = order
                        isExist = True
                        break
                    index = index + 1
                if not isExist:
                    if len(self.data[symbol]['order']) > limit:
                        self.data[symbol]['order'].pop(-1)
                    self.data[symbol]['order'].insert(0, order)
        except Exception as e:
            logging.error(f'Wootrade get order error: {e}')

    def _get_position(self, symbol: str, params: dict):
        try:
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
            params = params['data']['positions']
            base = symbol.split('_')[0]
            quote = symbol.split('_')[1]
            if base in params.keys():
                self.data['wallet'][base].update({
                    'balance': params[base]['holding'],
                    'frozen': params[base]['outstanding_holding']
                })
            if quote in params.keys():
                self.data['wallet'][quote].update({
                    'balance': params[quote]['holding'],
                    'frozen': params[quote]['outstanding_holding']
                })
        except Exception as e:
            logging.error(f'Wootrade get wallet balance error: {e}')

    def on_message(self, symbol: str, private: bool):
        # Support types
        # ticker / book / trade / order_update / position
        def _message():
            try:
                ws = self._connect(symbol, private)
                if ws is None:
                    logging.error('Binance public does not connected, and connection closed!')
                else:
                    while True:
                        recv = json.loads(ws.recv())
                        if 'error' in recv and recv['error']:
                            # identify error in receive
                            logging.error(f'Wootrade Sub error: {recv["data"]}')
                            break
                        elif recv['event'] == 'ticker':
                            self._get_price(symbol, recv)
                        elif recv['event'] == 'PING':  # receive ping from server and send pong
                            print(recv)
                            ws.send(json.dumps({'event': 'PONG'}))
                        else:
                            print(recv)
            except Exception as e:
                logging.error(f'Wootrade Sub public error {e}: try to connect again')
                _message()

        def _auth_message():
            try:
                ws = self._connect(symbol, private)
                if ws is None:
                    logging.error('Binance auth does not connected, and connection closed!')
                else:
                    while True:
                        recv = json.loads(ws.recv())
                        if 'error' in recv and recv['error']:
                            # identify error in receive
                            logging.error(f'Wootrade Sub error: {recv["data"]}')
                            break
                        else:
                            switch = {
                                'TRADE': self._get_trade,
                                'BOOK': self._get_orderbook,
                                'ORDER_UPDATE': self._get_order,
                                'POSITIONS': self._get_position,
                                'PING': lambda sym, re: ws.send(json.dumps({'event': 'PONG'}))
                            }
                            switch.get(recv['event'], lambda params: print(recv))(symbol, recv)
            except Exception as e:
                logging.error(f'Wootrade Sub public error {e}: try to connect again')
                _auth_message()

        if private:
            Thread(target=_auth_message).start()
        else:
            Thread(target=_message).start()

    def sub_price(self, symbol: str):
        self.data[symbol]['price'] = None
        self.on_message(symbol, private=False)

    def sub_orderbook(self, symbol: str):
        self.data[symbol]['orderbook'] = None
        self.on_message(symbol, private=True)

    def sub_kline(self, symbol: str):
        self.data[symbol]['kline'] = []
        pass

    def sub_trade(self, symbol: str):
        self.data[symbol]['trade'] = None
        self.on_message(symbol, private=True)

    def sub_order(self, symbol: str):
        self.data[symbol]['order'] = []
        self.on_message(symbol, private=True)

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
        self.on_message(symbol, private=True)


# wootrade = WootradeWs()

# if __name__ == '__main__':
#     b = WootradeWs()
#     # b.sub_price('BTC_USDT')
#     b.sub_price('XPO_USDT')
#     while True:
#         time.sleep(3)
#         print(b.data)


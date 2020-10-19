# -*- coding: utf-8 -*-
"""
binance公共接口
2020/10/10 hlq
"""
import requests
import time
import math


class BinancePublic:
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        """ convert symbol to appropriate format """
        return ''.join(symbol.split('_'))

    def get_price_precision(self, symbol: str):
        try:
            url = self.urlbase + '/api/v3/exchangeInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp['symbols']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        return int(abs(math.log10(float(ticker['filters'][0]['tickSize']))))
            else:
                print(f'Binance public error: {resp.json()["message"]}')
        except Exception as e:
            print(f'Binance public get price precision error: {e}')

    def get_price_increment(self, symbol: str):
        try:
            url = self.urlbase + '/api/v3/exchangeInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp['symbols']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        return float(ticker['filters'][0]['tickSize'])
            else:
                print(f'Binance public error: {resp.json()["message"]}')
        except Exception as e:
            print(f'Binance public get price increment error: {e}')

    def get_amount_precision(self, symbol: str):
        try:
            url = self.urlbase + '/api/v3/exchangeInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp['symbols']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        return int(abs(math.log10(float(ticker['filters'][2]['minQty']))))
            else:
                print(f'Binance public error: {resp.json()["message"]}')
        except Exception as e:
            print("Binance public get amount precision error: %s" % e)

    def get_amount_increment(self, symbol: str):
        try:
            url = self.urlbase + '/api/v3/exchangeInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp['symbols']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        return float(ticker['filters'][2]['minQty'])
            else:
                print(f'Bitmart public error: {resp.json()["message"]}')
        except Exception as e:
            print(f'Bitmart public get min amount error: {e}')

    def get_price(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/ticker/price?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url)
            price = 0.0
            if resp.status_code == 200:
                resp = resp.json()
                price = float(resp['price'])
            return price
        except Exception as e:
            print(f'Binance public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/ticker/24hr?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url)
            result = {}
            if resp.status_code == 200:
                ticker = resp.json()
                result = {
                    'symbol': ticker['symbol'],
                    'last_price': float(ticker['lastPrice']),
                    'quote_volume': float(ticker['quoteVolume']),
                    'base_volume': float(ticker['volume']),
                    'highest_price': float(ticker['highPrice']),
                    'lowest_price': float(ticker['lowPrice']),
                    'open_price': float(ticker['openPrice']),
                    'close_price': float(ticker['prevClosePrice']),
                    'ask_1': float(ticker['askPrice']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bidPrice']),
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['priceChangePercent']),
                    'url': url,
                }
            else:
                print(f'Binance public request error: {resp.json()}')
            return result
        except Exception as e:
            print(f'Binance public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/depth?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url)
            orderbook = {
                'buys': [],
                'sells': []
            }
            if resp.status_code == 200:
                resp = resp.json()
                for item in resp['asks']:
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': None,
                        'price': float(item[0]),
                        'count': None
                    })
                for item in resp['bids']:
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': None,
                        'price': float(item[0]),
                        'count': None
                    })
            else:
                print(f'Binance public request error: {resp.json()}')
            return orderbook
        except Exception as e:
            print(f'Binance public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/trades?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'count': float(trade['qty']),
                        'order_time': round(trade['time'] / 1000),
                        'price': float(trade['price']),
                        'amount': float(trade['qty'])*float(trade['price']),
                        'type': None
                    })
                return trades
            else:
                print(f'Binance public request error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'Binance public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            end_time = round(time.time())
            start_time = end_time - time_period
            url = self.urlbase + f'/api/v3/klines?symbol={self._symbol_convert(symbol)}' \
                                 f'&interval={interval}m&startTime={start_time}&endTime={end_time}'
            resp = requests.get(url)
            lines = []
            if resp.status_code == 200:
                resp = resp.json()
                for line in resp:
                    lines.append({
                        'timestamp': round(line[0] / 1000),
                        'volume': float(line[5]),
                        'open_price': float(line[1]),
                        'current_price': float(line[4]),
                        'lowest_price': float(line[3]),
                        'highest_price': float(line[2])
                    })
            else:
                print(f'Binance public request error: {resp.json()}')
            return lines
        except Exception as e:
            print(f'Binance public get kline error: {e}')


if __name__ == '__main__':
    binance = BinancePublic('https://api.binance.com')
    print(binance.get_price_precision('BTC_USDT'))
    print(binance.get_price_increment('BTC_USDT'))
    print(binance.get_amount_precision('BTC_USDT'))
    print(binance.get_amount_increment('BTC_USDT'))
    # print(binance.get_price('BTC_USDT'))
    # print(binance.get_ticker('BTC_USDT'))
    # print(binance.get_orderbook('BTC_USDT'))
    # print(binance.get_trades('BTC_USDT'))
    # print(binance.get_kline('BTC_USDT'))

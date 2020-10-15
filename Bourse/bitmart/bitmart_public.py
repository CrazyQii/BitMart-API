# -*- coding: utf-8 -*-
"""
bitmart spot public API
2020/10/9 hlq
"""
import requests
import traceback
import time
import math


class BitmartPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price_precision(self, symbol: str):
        """
        accuracy (decimal places), used to query k-line and depth
        最大价格精度(小数位) 用来查询 k 线和深度
        """
        try:
            url = self.urlbase + '/spot/v1/symbols/details'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                for ticker in resp['data']['symbols']:
                    if ticker['symbol'] == symbol:
                        return int(ticker['price_max_precision'])
            else:
                print(f'Bitmart public request error: {resp["message"]}')
        except Exception as e:
            print(f'Bitmart public get price increment error: {e}')

    def get_price_increment(self, symbol: str):
        """
        The minimum order quantity is also the minimum order quantity increment
        最小下单量，也是最小下单量增量
        """
        try:
            url = self.urlbase + '/spot/v1/symbols/details'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                for ticker in resp['data']['symbols']:
                    if ticker['symbol'] == symbol:
                        return float(ticker['quote_increment'])
            else:
                print(f'Bitmart public request error: {resp["message"]}')
        except Exception as e:
            print(f'Bitmart public get price increment error: {e}')

    def get_amount_precision(self, symbol: str):
        """
        minimum order quantity accuracy
        下单数量精度
        """
        try:
            url = self.urlbase + '/spot/v1/symbols/details'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                for ticker in resp['data']['symbols']:
                    if ticker['symbol'] == symbol:
                        return int(abs(math.log10(float(ticker['base_min_size']))))
            else:
                print(f'Bitmart public request error: {resp["message"]}')
        except Exception as e:
            print("Bitmart public get amount precision error: %s" % e)

    def get_amount_increment(self, symbol: str):
        """
        minimum order quantity increment
        最小下单数量增量
        """
        try:
            url = self.urlbase + '/spot/v1/symbols/details'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                for ticker in resp['data']['symbols']:
                    if ticker['symbol'] == symbol:
                        return float(ticker['base_min_size'])
            else:
                print(f'Bitmart public request error: {resp["message"]}')
        except Exception as e:
            print(f'Bitmart public get min amount error: {e}')

    def get_price(self, symbol: str):
        """ Get the latest trade price of specified ticker """
        try:
            url = self.urlbase + f'/spot/v1/symbols/trades?symbol={symbol}'
            resp = requests.get(url).json()
            price = 0.0
            if resp['code'] == 1000:
                price = float(resp['data']['trades'][0]['price'])
            else:
                print(f'Bitmart public request error: {resp["message"]}')
            return price
        except Exception as e:
            print(f'Bitmart public get price error: {e}')

    def get_ticker(self, symbol: str):
        """
        Ticker is an overview of the market status of a trading pair,
        including the latest trade price, top bid and ask prices
        and 24-hour trading volume
        """
        try:
            url = self.urlbase + f'/spot/v1/ticker?symbol={symbol}'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                ticker = resp['data']['tickers'][0]
                return {
                    'symbol': ticker['symbol'],
                    'last_price': float(ticker['last_price']),
                    'quote_volume': float(ticker['quote_volume_24h']),
                    'base_volume': float(ticker['base_volume_24h']),
                    'highest_price': float(ticker['high_24h']),
                    'lowest_price': float(ticker['low_24h']),
                    'open_price': float(ticker['open_24h']),
                    'close_price': float(ticker['close_24h']),
                    'ask_1': float(ticker['best_ask']),
                    'ask_1_amount': float(ticker['best_ask_size']),
                    'bid_1': float(ticker['best_bid']),
                    'bid_1_amount': float(ticker['best_bid_size']),
                    'fluctuation': float(ticker['fluctuation']),
                    'url': ticker['url'],
                }
            else:
                print(f'Bitmart public request error: {resp["message"]}')
        except Exception as e:
            print(f'Bitmart public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        """
        Get full depth of trading pairs.
        """
        try:
            max_precision = self.get_price_precision(symbol)
            url = self.urlbase + f'/spot/v1/symbols/book?symbol={symbol}&precision={max_precision}'
            resp = requests.get(url).json()
            orderbook = {'buys': [], 'sells': []}
            if resp['code'] == 1000:
                for item in resp['data']['buys']:
                    orderbook['buys'].append({
                        'amount': float(item['amount']),
                        'total': float(item['total']),
                        'price': float(item['price']),
                        'count': int(item['count'])
                    })
                for item in resp['data']['sells']:
                    orderbook['sells'].append({
                        'amount': float(item['amount']),
                        'total': float(item['total']),
                        'price': float(item['price']),
                        'count': int(item['count'])
                    })
            else:
                print(f'Bitmart public request error: {resp["message"]}')
            return orderbook
        except Exception as e:
            print(f'Bitmart public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        """
        Get the latest trade records of the specified trading pair
        """
        try:
            url = self.urlbase + f'/spot/v1/symbols/trades?symbol={symbol}'
            trades = []
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                for trade in resp['data']['trades']:
                    trades.append({
                        'amount': float(trade['amount']),
                        'order_time': round(trade['order_time'] / 1000),
                        'price': float(trade['price']),
                        'count': float(trade['count']),
                        'type': trade['type']
                    })
            else:
                print(f'Bitmart public request error: {resp["message"]}')
            return trades
        except Exception as e:
            print(f'Bitmart public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        """
        Get k-line data within a specified time range of a specified trading pair
        """
        end_time = round(time.time())
        start_time = end_time - time_period
        try:
            url = self.urlbase + f'/spot/v1/symbols/kline?symbol={symbol}&step={interval}&from={start_time}&to={end_time}'

            resp = requests.get(url).json()
            lines = []
            if resp['code'] == 1000:
                for line in resp['data']['klines']:
                    lines.append({
                        'timestamp': line['timestamp'],
                        'open': float(line['open']),
                        'high': float(line['high']),
                        'low': float(line['low']),
                        'volume': float(line['volume']),
                        'last_price': float(line['last_price'])
                    })
            else:
                print(f'Bitmart public request error: {resp["message"]}')
            return lines
        except Exception as e:
            print(f'Bitmart public get kline error: {e}')


if __name__ == '__main__':
    bit = BitmartPublic('https://api-cloud.bitmart.info')
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))

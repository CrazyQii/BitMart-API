# -*- coding: utf-8 -*-
"""
bitmart spot public API
2020/10/9 hlq
"""
import os
import requests
import time
import math
import json

cur_path = os.path.abspath(os.path.dirname(__file__))


class BitmartPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_symbols_info(self):
        """ initialize symbol details in json """
        try:
            url = self.urlbase + '/spot/v1/symbols/details'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                data = {}
                for ticker in resp['data']['symbols']:
                    data.update({
                        ticker['symbol']: {
                            'min_amount': float(ticker['base_min_size']),  # 最小下单数量
                            'min_notional': float(ticker['min_buy_amount']),  # 最小下单金额
                            'amount_increment': float(ticker['quote_increment']),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, float(ticker['price_max_precision'])),
                                                     int(ticker['price_max_precision'])),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['base_min_size'])))),  # 数量小数位
                            'price_digit': int(ticker['price_max_precision'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Bitmart batch load symbols error')
        except Exception as e:
            print(f'Bitmart batch load symbols exception {e}')

    def get_symbol_info(self, symbol: str):
        try:
            symbol_info = dict()
            with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                symbols_detail = json.load(f)
            f.close()

            if symbol not in symbols_detail.keys():
                # update symbols detail
                self._load_symbols_info()

                with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                    symbols_detail = json.load(f)
                f.close()

            symbol_info['symbol'] = symbol
            symbol_info['min_amount'] = symbols_detail[symbol]['min_amount']
            symbol_info['min_notional'] = symbols_detail[symbol]['min_notional']
            symbol_info['amount_increment'] = symbols_detail[symbol]['amount_increment']
            symbol_info['price_increment'] = symbols_detail[symbol]['price_increment']
            symbol_info['amount_digit'] = symbols_detail[symbol]['amount_digit']
            symbol_info['price_digit'] = symbols_detail[symbol]['price_digit']
            return symbol_info
        except Exception as e:
            print(f'Bitmart get symbol info error: {e}')

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
            ticker = {}
            if resp['code'] == 1000:
                ticker = resp['data']['tickers'][0]
                ticker = {
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
            return ticker
        except Exception as e:
            print(f'Bitmart public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        """
        Get full depth of trading pairs.
        """
        try:
            max_precision = self.get_symbol_info(symbol)['price_digit']
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
    bit = BitmartPublic('https://api-cloud.bitmart.news')
    # print(bit.get_symbol_info('BTC_USDT'))
    print(bit.get_price('BTC_USDT'))
    print(bit.get_ticker('BTC_USDT'))
    print(bit.get_orderbook('BTC_USDT'))
    print(bit.get_trades('BTC_USDT'))
    print(bit.get_kline('BTC_USDT'))

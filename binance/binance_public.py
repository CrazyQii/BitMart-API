# -*- coding: utf-8 -*-
"""
binance公共接口
2020-10-10 hlq
"""
import requests
import traceback
import time


class BinancePublic:
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        """ convert symbol to appropriate format """
        return ''.join(symbol.split('_'))

    def _request(self, method, url, params=None, data=None, headers=None):
        try:
            resp = requests.request(method, url, params=params, data=data, headers=headers)

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    'code': resp.status_code,
                    'method': method,
                    'url': url,
                    'data': data,
                    'msg': resp.text
                }
                return False, error
        except requests.exceptions.RequestException as e:
            error = {
                'method': method,
                'url': url,
                'data': data,
                'traceback': traceback.format_exc(),
                'error': e
            }
            return False, error

    def _output(self, function_name, content):
        """ output error info """
        info = {
            'function_name': function_name,
            'content': content
        }
        print(info)

    def get_price(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/ticker/price?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                return float(content['price'])
            else:
                self._output('get_price', content)
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/depth?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                orderbook = {
                    'bids': [],
                    'asks': []
                }
                for item in content['bids']:
                    orderbook['bids'].append([float(item[0]), float(item[1])])
                for item in content['asks']:
                    orderbook['asks'].append([float(item[0]), float(item[1])])
                return orderbook
            else:
                self._output('get_orderbook', content)
        except Exception as e:
            print(e)

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/ticker/24hr?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                ticker = content
                result = {
                    'symbol_id': ticker['symbol'],
                    'url': url,
                    'base_volume': ticker['volume'],
                    'volume': ticker['quoteVolume'],
                    'fluctuation': ticker['priceChange'],
                    'bid_1_amount': None,
                    'bid_1': ticker['bidPrice'],
                    'ask_1_amount': None,
                    'ask_1': ticker['askPrice'],
                    'current_price': ticker['lastPrice'],
                    'lowest_price': ticker['lowPrice'],
                    'highest_price': ticker['highPrice']
                }
                return result
            else:
                self._output('get_ticker', content)
        except Exception as e:
            print(e)

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v3/trades?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content:
                    trades.append({
                        'count': float(trade['qty']),
                        'amount': float(trade['qty'])*float(trade['price']),
                        'type': None,
                        'price': float(trade['price']),
                        'order_time': trade['time']
                    })
                return trades
            else:
                self._output('get_trades', content)
        except Exception as e:
            print(e)

    def get_kline(self, symbol: str, time_period=60):
        if time_period % 60 != 0:
            raise Exception('time period must be the 1m, 5m, 30m and so on')
        try:
            end = round(time.time())
            start = end - time_period
            url = self.urlbase + f'/api/v3/klines?symbol={self._symbol_convert(symbol)}&interval={int(time_period/60)}m'

            is_ok, content = self._request('GET', url)
            if is_ok:
                lines = []
                for line in content:
                    lines.append({
                        'timestamp': line[0],
                        'volume': line[5],
                        'open_price': line[1],
                        'current_price': line[4],
                        'lowest_price': line[3],
                        'highest_price': line[2]
                    })
                return lines
            else:
                self._output('get_kline', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    binance = BinancePublic('https://api.binance.com')
    # print(binance.get_price('BTC_USDT'))
    # print(binance.get_orderbook('BTC_USDT'))
    # print(binance.get_ticker('BTC_USDT'))
    # print(binance.get_trades('BTC_USDT'))
    # print(binance.get_kline('BTC_USDT'))

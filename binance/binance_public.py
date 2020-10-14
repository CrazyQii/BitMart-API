# -*- coding: utf-8 -*-
"""
binance公共接口
2020/10/10 hlq
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
        """
        Get the latest trade price of the specified ticker
        """
        try:
            url = self.urlbase + f'/api/v3/ticker/price?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                return float(content['price'])
            else:
                self._output('get_price', content)
                return None
        except Exception as e:
            print(e)
            return None

    def get_ticker(self, symbol: str):
        """
        Ticker is an overview of the market status of a trading pair,
        including the latest trade price, top bid and ask prices
        and 24-hour trading volume
        """
        try:
            url = self.urlbase + f'/api/v3/ticker/24hr?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            result = {}
            if is_ok:
                ticker = content
                result = {
                    'symbol_id': ticker['symbol'],
                    'url': url,
                    'base_volume': float(ticker['volume']),
                    'volume': float(ticker['quoteVolume']),
                    'fluctuation': float(ticker['priceChange']),
                    'bid_1_amount': None,
                    'bid_1': float(ticker['bidPrice']),
                    'ask_1_amount': None,
                    'ask_1': float(ticker['askPrice']),
                    'current_price': float(ticker['lastPrice']),
                    'lowest_price': float(ticker['lowPrice']),
                    'highest_price': float(ticker['highPrice'])
                }
            else:
                self._output('get_ticker', content)
            return result
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str):
        """
        Get full depth of trading pairs.
        """
        try:
            url = self.urlbase + f'/api/v3/depth?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            orderbook = {
                'bids': [],
                'asks': []
            }
            if is_ok:
                for item in content['bids']:
                    orderbook['bids'].append([float(item[0]), float(item[1])])
                for item in content['asks']:
                    orderbook['asks'].append([float(item[0]), float(item[1])])
            else:
                self._output('get_orderbook', content)
            return orderbook
        except Exception as e:
            print(e)
            return None

    def get_trades(self, symbol: str):
        """
        Get the latest trade records of the specified trading pair
        """
        try:
            url = self.urlbase + f'/api/v3/trades?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            trades = []
            if is_ok:
                for trade in content:
                    trades.append({
                        'count': float(trade['qty']),
                        'amount': float(trade['qty'])*float(trade['price']),
                        'type': None,
                        'price': float(trade['price']),
                        'order_time': round(trade['time'] / 1000)
                    })
                return trades
            else:
                self._output("get_trades", content)
                return {"price": "0.0", "amount": "0.0"}
        except Exception as e:
            print(e)
            return None

    def get_kline(self, symbol: str, time_period=60):
        """
        Get k-line data within a specified time range of a specified trading pair
        """
        if time_period % 60 != 0:
            raise Exception('time period must be the 1m, 5m, 30m and so on')
        try:
            url = self.urlbase + f'/api/v3/klines?symbol={self._symbol_convert(symbol)}&interval={int(time_period/60)}m'
            is_ok, content = self._request('GET', url)
            lines = []
            if is_ok:
                for line in content:
                    lines.append({
                        'timestamp': round(line[0] / 1000),
                        'volume': float(line[5]),
                        'open_price': float(line[1]),
                        'current_price': float(line[4]),
                        'lowest_price': float(line[3]),
                        'highest_price': float(line[2])
                    })
            else:
                self._output('get_kline', content)
            return lines
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    binance = BinancePublic('https://api.binance.com')
    # print(binance.get_price('BTC_USDT'))
    # print(binance.get_ticker('BTC_USDT'))
    # print(binance.get_orderbook('BTC_USDT'))
    # print(binance.get_trades('BTC_USDT'))
    # print(binance.get_kline('BTC_USDT'))

# -*- coding: utf-8 -*-
"""
bitmart spot public API
2020/10/9 hlq
"""
import requests
import traceback
import time


class BitmartPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

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

    def get_price_precision(self, symbol: str):
        """
        accuracy (decimal places), used to query k-line and depth
        最大价格精度(小数位) 用来查询 k 线和深度
        """
        try:
            url = self.urlbase + f'/spot/v1/symbols/details?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                return content

    def get_price(self, symbol: str):
        """ Get the latest trade price of specified ticker """
        try:
            url = self.urlbase + f'/spot/v1/ticker?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                return float(content['data']['tickers'][0]['last_price'])
            else:
                self._output('get_price', content)
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
            url = self.urlbase + f'/spot/v1/ticker?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            result = {}
            if is_ok:
                ticker = content['data']['tickers'][0]
                result = {
                    'symbol_id': ticker['symbol'],
                    'url': ticker['url'],
                    'base_volume': float(ticker['base_volume_24h']),
                    'volume': float(ticker['quote_volume_24h']),
                    'fluctuation': float(ticker['fluctuation']),
                    'bid_1_amount': float(ticker['best_bid_size']),
                    'bid_1': float(ticker['best_bid']),
                    'ask_1_amount': float(ticker['best_ask_size']),
                    'ask_1': float(ticker['best_ask']),
                    'current_price': float(ticker['last_price']),
                    'lowest_price': float(ticker['low_24h']),
                    'highest_price': float(ticker['high_24h'])
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
            url = self.urlbase + f'/spot/v1/symbols/book?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            orderbook = {
                'bids': [],
                'asks': []
            }
            if is_ok:
                for item in content['data']['buys']:
                    orderbook['bids'].append([float(item['price']), float(item['amount'])])
                for item in content['data']['sells']:
                    orderbook['asks'].append([float(item['price']), float(item['amount'])])
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
            url = self.urlbase + f'/spot/v1/symbols/trades?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content['data']['trades']:
                    trades.append({
                        'count': float(trade['count']),
                        'amount': float(trade['amount']),
                        'type': trade['type'],
                        'price': float(trade['price']),
                        'order_time': round(trade['order_time'] / 1000)
                    })
                return trades
            else:
                self._output('get_trades', content)
                return {"price": "0.0", "amount": "0.0"}
        except Exception as e:
            print(e)
            return None

    def get_kline(self, symbol: str, time_period=3600):
        """
        Get k-line data within a specified time range of a specified trading pair
        """
        if time_period % 60 != 0:
            raise Exception('time period must be the integer multiple of 60')
        try:
            end = round(time.time())
            start = end - time_period
            url = self.urlbase + f'/spot/v1/symbols/kline?symbol={symbol}&step={int(time_period/60)}&from={start}&to={end}'

            is_ok, content = self._request('GET', url)
            lines = []
            if is_ok:
                for line in content['data']['klines']:
                    lines.append({
                        'timestamp': line['timestamp'],
                        'volume': float(line['volume']),
                        'open_price': float(line['open']),
                        'current_price': float(line['last_price']),
                        'lowest_price': float(line['low']),
                        'highest_price': float(line['high'])
                    })
                return lines
            else:
                self._output('get_kline', content)
            return lines
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    bit = BitmartPublic('https://api-cloud.bitmart.info')
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))

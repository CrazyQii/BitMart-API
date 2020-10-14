# -*- coding: utf-8 -*-
"""
HuoBi spot public api
2020/10/13 hlq
"""

import requests
import traceback


class HuoPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

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
            url = self.urlbase + f'/market/detail/merged?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                content = content['tick']
                return float(content['close'])
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
            url = self.urlbase + f'/market/detail/merged?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            result = {}
            if is_ok:
                content = content['tick']
                result = {
                    'symbol_id': symbol,
                    'url': url,
                    'base_volume': float(content['amount']),
                    'volume': float(content['vol']),
                    'fluctuation': None,
                    'bid_1_amount': float(content['bid'][1]),
                    'bid_1': float(content['bid'][0]),
                    'ask_1_amount': float(content['ask'][1]),
                    'ask_1': float(content['ask'][0]),
                    'current_price': float(content['close']),
                    'lowest_price': float(content['low']),
                    'highest_price': float(content['high'])
                }
            else:
                self._output('get_ticker', content)
            return result
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str, step=0):
        """
        Get full depth of trading pairs.
        """
        try:
            url = self.urlbase + f'/market/depth?symbol={self._symbol_convert(symbol)}&type=step{step}'
            is_ok, content = self._request('GET', url)
            orderbook = {
                'bids': [],
                'asks': []
            }
            if is_ok:
                content = content['tick']
                orderbook = {
                    'bids': content['bids'],
                    'asks': content['asks']
                }
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
            url = self.urlbase + f'/market/history/trade?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                content = content['data']
                trades = []
                for trade in content:
                    trades.append({
                        'count': float(trade['data'][0]['amount']),
                        'amount': float(trade['data'][0]['amount']) * float(trade['data'][0]['price']),
                        'type': trade['data'][0]['direction'],
                        'price': float(trade['data'][0]['price']),
                        'order_time': round(trade['data'][0]['ts'] / 1000)
                    })
                return trades
            else:
                self._output('get_trades', content)
                return {"price": "0.0", "amount": "0.0"}
        except Exception as e:
            print(e)
            return None

    def get_kline(self, symbol: str, time_period=60):
        """
        Get k-line data within a specified time range of a specified trading pair
        """
        try:
            url = self.urlbase + f'/market/history/kline?symbol={self._symbol_convert(symbol)}&period={int(time_period/60)}min'

            is_ok, content = self._request('GET', url)
            lines = []
            if is_ok:
                content = content['data']
                for line in content:
                    lines.append({
                        'timestamp': line['id'],
                        'volume': float(line['vol']),
                        'open_price': float(line['open']),
                        'current_price': float(line['close']),
                        'lowest_price': float(line['low']),
                        'highest_price': float(line['high'])
                    })
            else:
                self._output('get_trades', content)
            return lines
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    huo = HuoPublic('https://api.huobi.pro')
    # print(huo.get_price('BTC_USDT'))
    # print(huo.get_ticker('BTC_USDT'))
    # print(huo.get_orderbook('BTC_USDT'))
    # print(huo.get_trades('BTC_USDT'))
    # print(huo.get_kline('BTC_USDT'))


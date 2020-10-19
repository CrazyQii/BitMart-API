# -*- coding: utf-8 -*-
"""
hoo spot public API
2020/9/28 hlq
"""
import requests
import traceback


class HooPublic:
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        """ convert symbol to appropriate format """
        return '-'.join(symbol.split('_'))

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
            url = self.urlbase + '/open/v1/tickers/market'
            is_ok, content = self._request('GET', url)
            if is_ok:
                for ticker in content['data']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        return float(ticker['price'])
                return None
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
            url = self.urlbase + '/open/v1/tickers/market'
            is_ok, content = self._request('GET', url)
            result = {}
            if is_ok:
                for ticker in content['data']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        result = {
                            'symbol_id': symbol,
                            'url': url,
                            'base_volume': None,
                            'volume': float(ticker['volume']),
                            'fluctuation': float(ticker['change']),
                            'bid_1_amount': None,
                            'bid_1': None,
                            'ask_1_amount': None,
                            'ask_1': None,
                            'current_price': float(ticker['price']),
                            'lowest_price': float(ticker['low']),
                            'highest_price': float(ticker['high'])
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
            url = self.urlbase + f'/open/v1/depth/market?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            orderbook = {
                'bids': [],
                'asks': []
            }
            if is_ok:
                for item in content['data']['bids']:
                    orderbook['bids'].append([float(item['price']), float(item['quantity'])])
                for item in content['data']['asks']:
                    orderbook['asks'].append([float(item['price']), float(item['quantity'])])
                return orderbook
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
            url = self.urlbase + f'/open/v1/trade/market?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content['data']:
                    trades.append({
                        'count': float(trade['volume']),
                        'amount': float(trade['amount']),
                        'type': 'buy' if trade['side'] == 1 else 'sell',
                        'price': float(trade['price']),
                        'order_time': round(trade['time'] / 1000)
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
            url = self.urlbase + f'/open/v1/kline/market?symbol={self._symbol_convert(symbol)}&type={int(time_period/60)}Min'

            is_ok, content = self._request('GET', url)
            lines = []
            if is_ok:
                for line in content['data']:
                    lines.append({
                        'timestamp': line['time'],
                        'volume': float(line['volume']),
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
    hoo = HooPublic('https://api.hoolgd.com')
    # print(hoo.get_price('BTC_USDT'))
    # print(hoo.get_ticker('BTC_USDT'))
    # print(hoo.get_orderbook('BTC_USDT'))
    # print(hoo.get_trades('BTC_USDT'))
    # print(hoo.get_kline('BTC_USDT'))

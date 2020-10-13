# -*- coding: utf-8 -*-
"""
hoo公共接口
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
        try:
            url = self.urlbase + '/open/v1/tickers/market'
            is_ok, content = self._request('GET', url)
            if is_ok:
                for ticker in content['data']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        return ticker['price']
                return False
            else:
                self._output('get_price', content)
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/open/v1/depth/market?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                orderbook = {
                    'bids': [],
                    'asks': []
                }
                for item in content['data']['bids']:
                    orderbook['bids'].append([float(item['price']), float(item['quantity'])])
                for item in content['data']['asks']:
                    orderbook['asks'].append([float(item['price']), float(item['quantity'])])
                return orderbook
            else:
                self._output('get_orderbook', content)
        except Exception as e:
            print(e)

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/open/v1/tickers/market'
            is_ok, content = self._request('GET', url)
            if is_ok:
                for ticker in content['data']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        result = {
                            'bid_1_amount': None,
                            'symbol_id': symbol,
                            'url': url,
                            'fluctuation': ticker['change'],
                            'base_volume': None,
                            'ask_1_amount': None,
                            'volume': ticker['volume'],
                            'current_price': ticker['price'],
                            'bid_1': None,
                            'lowest_price': ticker['low'],
                            'ask_1': None,
                            'highest_price': ticker['high']
                        }
                        return result
                return None
            else:
                self._output('get_ticker', content)
        except Exception as e:
            print(e)

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/open/v1/trade/market?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content['data']:
                    trades.append({
                        'count': trade['volume'],
                        'amount': trade['amount'],
                        'type': 'buy' if trade['side'] == 1 else 'sell',
                        'price': trade['price'],
                        'order_time': trade['time']
                    })
                return trades
            else:
                self._output('get_trades', content)
        except Exception as e:
            print(e)

    def get_kline(self, symbol: str, time_period=60):
        try:
            url = self.urlbase + f'/open/v1/kline/market?symbol={self._symbol_convert(symbol)}&type={int(time_period/60)}Min'

            is_ok, content = self._request('GET', url)
            if is_ok:
                lines = []
                for line in content['data']:
                    lines.append({
                        'timestamp': line['time'],
                        'volume': line['volume'],
                        'open_price': line['open'],
                        'current_price': line['close'],
                        'lowest_price': line['low'],
                        'highest_price': line['high']
                    })

                return lines
            else:
                self._output('get_trades', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    hoo = HooPublic('https://api.hoolgd.com')
    print(hoo.get_price('BTC_USDT'))
    # print(hoo.get_orderbook('BTC_USDT'))
    # print(hoo.get_ticker('BTC_USDT'))
    # print(hoo.get_trades('BTC_USDT'))
    # print(hoo.get_kline('BTC_USDT'))

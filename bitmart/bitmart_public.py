# -*- coding: utf-8 -*-
"""
bitmart公共接口
2020-10-9 hlq
"""
import requests
import traceback
import time


class BitmartPublic:
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

    def get_price(self, symbol: str):
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

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/v1/symbols/book?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                orderbook = {
                    'bids': [],
                    'asks': []
                }
                for item in content['data']['buys']:
                    orderbook['bids'].append([float(item['price']), float(item['amount'])])
                for item in content['data']['sells']:
                    orderbook['asks'].append([float(item['price']), float(item['amount'])])
                return orderbook
            else:
                self._output('get_orderbook', content)
        except Exception as e:
            print(e)

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/v1/ticker?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                ticker = content['data']['tickers'][0]
                result = {
                    'symbol_id': ticker['symbol'],
                    'url': ticker['url'],
                    'base_volume': ticker['base_volume_24h'],
                    'volume': ticker['quote_volume_24h'],
                    'fluctuation': ticker['fluctuation'],
                    'bid_1_amount': ticker['best_bid_size'],
                    'bid_1': ticker['best_bid'],
                    'ask_1_amount': ticker['best_ask_size'],
                    'ask_1': ticker['best_ask'],
                    'current_price': ticker['last_price'],
                    'lowest_price': ticker['low_24h'],
                    'highest_price': ticker['high_24h']
                }
                return result
            else:
                self._output('get_ticker', content)
        except Exception as e:
            print(e)

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/v1/symbols/trades?symbol={symbol}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content['data']['trades']:
                    trades.append({
                        'count': trade['count'],
                        'amount': trade['amount'],
                        'type': trade['type'],
                        'price': trade['price'],
                        'order_time': trade['order_time']
                    })
                return trades
            else:
                self._output('get_trades', content)
        except Exception as e:
            print(e)

    def get_kline(self, symbol: str, time_period=3600):
        if time_period % 60 != 0:
            raise Exception('time period must be the integer multiple of 60')
        try:
            end = round(time.time())
            start = end - time_period
            url = self.urlbase + f'/spot/v1/symbols/kline?symbol={symbol}&step={int(time_period/60)}&from={start}&to={end}'

            is_ok, content = self._request('GET', url)
            if is_ok:
                lines = []
                for line in content['data']['klines']:
                    lines.append({
                        'timestamp': line['timestamp'],
                        'volume': line['volume'],
                        'open_price': line['open'],
                        'current_price': line['last_price'],
                        'lowest_price': line['low'],
                        'highest_price': line['high']
                    })

                return lines
            else:
                self._output('get_kline', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    bit = BitmartPublic('https://api-cloud.bitmart.info')
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))

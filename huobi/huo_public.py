"""
HuoBi public api
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
        try:
            url = self.urlbase + f'/market/detail/merged?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                return content['close']
            else:
                self._output('get_price', content)
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str, step=0):
        try:
            url = self.urlbase + f'/market/depth?symbol={self._symbol_convert(symbol)}&step=step{step}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                orderbook = {
                    'bids': content['bids'],
                    'asks': content['asks']
                }
                return orderbook
            else:
                self._output('get_orderbook', content)
        except Exception as e:
            print(e)

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/market/detail/merged?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                result = {
                    'symbol_id': symbol,
                    'url': url,
                    'fluctuation': None,
                    'base_volume': content['amount'],
                    'volume': content['vol'],
                    'bid_1': content['bid'][0],
                    'bid_1_amount': content['bid'][1],
                    'ask_1': content['ask'][0],
                    'ask_1_amount': content['ask'][1],
                    'current_price': content['close'],
                    'lowest_price': content['low'],
                    'highest_price': content['high']
                }
                return result
            else:
                self._output('get_ticker', content)
        except Exception as e:
            print(e)

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/market/history/trade?symbol={self._symbol_convert(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content['data']:
                    trades.append({
                        'count': trade['amount'],
                        'amount': float(trade["amount"]) * float(trade["price"]),
                        'type': trade['direction'],
                        'price': trade['price'],
                        'order_time': trade['ts']
                    })
                return trades
            else:
                self._output('get_trades', content)
        except Exception as e:
            print(e)

    def get_kline(self, symbol: str, time_period=60):
        try:
            url = self.urlbase + f'/market/history/kline?symbol={self._symbol_convert(symbol)}&period={int(time_period/60)}Min'

            is_ok, content = self._request('GET', url)
            if is_ok:
                lines = []
                for line in content:
                    lines.append({
                        'timestamp': line['id'],
                        'volume': line['vol'],
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
    huo = HuoPublic('https://api.huobi.pro')
    print(huo.get_price('BTC_USDT'))
    print(huo.get_kline('BTC_USDT'))
    print(huo.get_orderbook('BTC_USDT'))
    print(huo.get_ticker('BTC_USDT'))
    print(huo.get_trades('BTC_USDT'))


# -*- coding: utf-8 -*-
"""
公共接口
2020/10/4 hlq
"""

import requests
import traceback


class QuoinePublic:
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

    def _product_id(self, symbol: str):
        """ get product's id by product's symbol """
        try:
            url = self.urlbase + '/products'
            is_ok, content = self._request('GET', url)
            if is_ok:
                for product in content:
                    if product['currency_pair_code'] == self._symbol_convert(symbol):
                        return product['id']
                return None
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def get_price(self, symbol: str):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/products/{self._product_id(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                return content['last_price_24h']
            else:
                self._output('get_products', content)
                return None
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/products/{self._product_id(symbol)}/price_levels'
            is_ok, content = self._request('GET', url)
            if is_ok:
                orderbook = {
                    'asks': [[float(i[0]), float(i[1])]for i in content['buy_price_levels']],
                    'bids': [[float(i[0]), float(i[1])] for i in content['sell_price_levels']],
                }
                return orderbook
            else:
                self._output('get_orderbook', content)
        except Exception as e:
            print(e)

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/products'
            is_ok, content = self._request('GET', url)
            if is_ok:
                for product in content:
                    if product['currency_pair_code'] == self._symbol_convert(symbol):
                        return {
                            'symbol_id': symbol,
                            'url': url,
                            'fluctuation': None,
                            'base_volume': None,
                            'bid_1_amount': product['market_bid'],
                            'ask_1_amount': product['market_ask'],
                            'volume': product['volume_24h'],
                            'ask_1': None,
                            'bid_1': None,
                            'current_price': product['last_price_24h'],
                            'lowest_price': None,
                            'highest_price': None
                        }
                return None
            else:
                self._output('get_ticker', content)
        except Exception as e:
            print(e)

    def get_trades(self, symbol: str):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/executions?product_id={self._product_id(symbol)}'
            is_ok, content = self._request('GET', url)
            if is_ok:
                trades = []
                for trade in content['models']:
                    trades.append({
                        'count': trade['quantity'],
                        'amount': float(trade['quantity']) * float(trade['price']),
                        'type': trade['taker_side'],
                        'price': trade['price'],
                        'order_time': trade['created_at']
                    })
                return trades
            else:
                self._output('get_trades', content)
        except Exception as e:
            print(e)

    def get_kline(self, symbol: str):
        """ cannot find it """
        pass


if __name__ == '__main__':
    quoine = QuoinePublic('https://api.liquid.com')
    # print(quoine.get_price('BTC_USDT'))
    # print(quoine.get_orderbook('BTC_USDT'))
    # print(quoine.get_ticker('BTC_USDT'))
    # print(quoine.get_trades('BTC_USDT'))

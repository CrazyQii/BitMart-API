# -*- coding: utf-8 -*-
"""
HuoBi spot public api
2020/10/13 hlq
"""

import requests


class HuoPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def get_price_precision(self, symbol: str):
        try:
            url = self.urlbase + '/v1/common/symbols'
            resp = requests.get(url).json()
            if resp['status'] == 'ok':
                for ticker in resp['data']:
                    if ticker['symbol'] == ''.join(symbol.split('_')).lower():
                        return int(ticker['price-precision'])
            else:
                print(f'Huobi public error: {resp["err-msg"]}')
        except Exception as e:
            print(f'Huobi public get price precision error: {e}')

    def get_price_increment(self, symbol: str):
        try:
            url = self.urlbase + '/v1/common/symbols'
            resp = requests.get(url).json()
            if resp['status'] == 'ok':
                for ticker in resp['data']:
                    if ticker['symbol'] == ''.join(symbol.split('_')).lower():
                        return round(0.1 ** ticker['price-precision'], ticker['price-precision'])
            else:
                print(f'Huobi public error: {resp["err-msg"]}')
        except Exception as e:
            print(f'Huobi public get price increment error: {e}')

    def get_amount_precision(self, symbol: str):
        try:
            url = self.urlbase + '/v1/common/symbols'
            resp = requests.get(url).json()
            if resp['status'] == 'ok':
                for ticker in resp['data']:
                    if ticker['symbol'] == ''.join(symbol.split('_')).lower():
                        return int(ticker['amount-precision'])
            else:
                print(f'Huobi public error: {resp["err-msg"]}')
        except Exception as e:
            print("Huobi public get amount precision error: %s" % e)

    def get_amount_increment(self, symbol: str):
        try:
            url = self.urlbase + '/v1/common/symbols'
            resp = requests.get(url).json()
            if resp['status'] == 'ok':
                for ticker in resp['data']:
                    if ticker['symbol'] == ''.join(symbol.split('_')).lower():
                        return round(0.1 ** ticker['amount-precision'], ticker['amount-precision'])
            else:
                print(f'Huobi public error: {resp["message"]}')
        except Exception as e:
            print(f'Huobi public get min amount error: {e}')

    def get_price(self, symbol: str):
        try:
            url = self.urlbase + f'/market/trade?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            price = 0.0
            if resp['status'] == 'ok':
                return float(resp['tick']['data'][0]['price'])
            else:
                print(f'Huobi public request error: {resp["err-msg"]}')
            return price
        except Exception as e:
            print(f'Huobi public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/market/tickers'
            resp = requests.get(url).json()
            result = {}
            if resp['status'] == 'ok':
                for ticker in resp['data']:
                    if ticker['symbol'] == self._symbol_convert(symbol):
                        result = {
                            'symbol': symbol,
                            'last_price': float(ticker['close']),
                            'quote_volume': float(ticker['vol']),
                            'base_volume': float(ticker['amount']),
                            'highest_price': float(ticker['high']),
                            'lowest_price': float(ticker['low']),
                            'open_price': float(ticker['open']),
                            'close_price': float(ticker['close']),
                            'ask_1': float(ticker['ask']),
                            'ask_1_amount': float(ticker['askSize']),
                            'bid_1': float(ticker['bid']),
                            'bid_1_amount': float(ticker['bidSize']),
                            'fluctuation': None,
                            'url': url
                        }
            else:
                print(f'Huobi public request error: {resp["err-msg"]}')
            return result
        except Exception as e:
            print(f'Huobi public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/market/depth?symbol={self._symbol_convert(symbol)}&type=step0'
            resp = requests.get(url).json()
            orderbook = {'buys': [], 'sells': []}
            if resp['status'] == 'ok':
                for item in resp['tick']['bids']:
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': None,
                        'price': float(item[0]),
                        'count': None
                    })
                for item in resp['tick']['asks']:
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': None,
                        'price': float(item[0]),
                        'count': None
                    })
            else:
                print(f'Huobi public request error: {resp["err-msg"]}')
            return orderbook
        except Exception as e:
            print(f'Huobi public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/market/history/trade?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            trades = []
            if resp['status'] == 'ok':
                for trade in resp['data']:
                    trades.append({
                        'amount': float(trade['data'][0]['amount']) * float(trade['data'][0]['price']),
                        'order_time': round(trade['data'][0]['ts'] / 1000),
                        'price': float(trade['data'][0]['price']),
                        'count': float(trade['data'][0]['amount']),
                        'type': trade['data'][0]['direction']
                    })
                return trades
            else:
                print(f'Bitmart public request error: {resp["err-msg"]}')
            return trades
        except Exception as e:
            print(f'Bitmart public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=60, interval=1):
        try:
            time_period = int(time_period / 60)
            url = self.urlbase + f'/market/history/kline?symbol={self._symbol_convert(symbol)}&period={time_period}min'

            resp = requests.get(url).json()
            lines = []
            if resp['status'] == 'ok':
                for line in resp['data']:
                    lines.append({
                        'timestamp': line['id'],
                        'open': float(line['open']),
                        'high': float(line['high']),
                        'lowe': float(line['low']),
                        'volume': float(line['vol']),
                        'last_price': float(line['close'])
                    })
            else:
                print(f'Huobi public request error: {resp["err-msg"]}')
            return lines
        except Exception as e:
            print(f'Huobi public get kline error: {e}')


if __name__ == '__main__':
    huo = HuoPublic('https://api.huobi.pro')
    print(huo.get_price_precision('BTC_USDT'))
    print(huo.get_price_increment('BTC_USDT'))
    print(huo.get_amount_precision('BTC_USDT'))
    print(huo.get_amount_increment('BTC_USDT'))
    # print(huo.get_price('BTC_USDT'))
    # print(huo.get_ticker('BTC_USDT'))
    # print(huo.get_orderbook('BTC_USDT'))
    # print(huo.get_trades('BTC_USDT'))
    # print(huo.get_kline('BTC_USDT'))


# -*- coding: utf-8 -*-
"""
HuoBi spot public api
2020/10/13 hlq
"""

import requests
import os
import json
import math

cur_path = os.path.abspath(os.path.dirname(__file__))


class HuoPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_')).lower()

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/v1/common/symbols'
            resp = requests.get(url).json()
            if resp['status'] == 'ok':
                data = {}
                for ticker in resp['data']:
                    data.update({
                        f'{ticker["base-currency"].upper()}_{ticker["quote-currency"].upper()}': {
                            'min_amount': float(ticker['limit-order-min-order-amt']),  # 最小下单数量
                            'min_notional': float(ticker['min-order-value']),  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, int(ticker['amount-precision'])), int(ticker['amount-precision'])),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, int(ticker['price-precision'])), int(ticker['price-precision'])),  # 价格最小变化
                            'amount_digit': int(ticker['amount-precision']),  # 数量小数位
                            'price_digit': int(ticker['price-precision'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Huobi batch load symbols error')
        except Exception as e:
            print(f'Huobi batch load symbols exception {e}')

    def get_symbol_info(self, symbol: str):
        symbols_detail = None
        # if file is exist
        try:
            with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                symbols_detail = json.load(f)
            f.close()
        except FileNotFoundError:
            self._load_symbols_info()
            with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                symbols_detail = json.load(f)
            f.close()
        except Exception as e:
            print(e)

        # read file
        try:
            if symbol not in symbols_detail.keys():
                # update symbols detail
                self._load_symbols_info()

                with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                    symbols_detail = json.load(f)
                f.close()

            symbol_info = dict()
            symbol_info['symbol'] = symbol
            symbol_info['min_amount'] = symbols_detail[symbol]['min_amount']
            symbol_info['min_notional'] = symbols_detail[symbol]['min_notional']
            symbol_info['amount_increment'] = symbols_detail[symbol]['amount_increment']
            symbol_info['price_increment'] = symbols_detail[symbol]['price_increment']
            symbol_info['amount_digit'] = symbols_detail[symbol]['amount_digit']
            symbol_info['price_digit'] = symbols_detail[symbol]['price_digit']
            return symbol_info
        except Exception as e:
            print(f'Huobi get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = 0.0
            trade = self.get_trades(symbol)
            if len(trade) > 0:
                price = trade[0]['price']
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
                print(f'Huobi public get ticker error: {resp["err-msg"]}')
            return result
        except Exception as e:
            print(f'Huobi public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/market/depth?symbol={self._symbol_convert(symbol)}&type=step0'
            resp = requests.get(url).json()
            orderbook = {'buys': [], 'sells': []}
            if resp['status'] == 'ok':
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['tick']['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': 1
                    })
                for item in resp['tick']['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': 1
                    })
            else:
                print(f'Huobi public get orderbook error: {resp["err-msg"]}')
            return orderbook
        except Exception as e:
            print(f'Huobi public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/market/history/trade?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            trades = []
            if resp['status'] == 'ok':
                for orders in resp['data']:
                    for trade in orders['data']:
                        trades.append({
                            'amount': float(trade['amount']) * float(trade['price']),
                            'order_time': round(trade['ts'] / 1000),
                            'price': float(trade['price']),
                            'count': float(trade['amount']),
                            'type': trade['direction']
                        })
                return trades
            else:
                print(f'Huobi public get trades error: {resp["err-msg"]}')
            return trades
        except Exception as e:
            print(f'Huobi public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=60, interval=1):
        try:
            url = self.urlbase + f'/market/history/kline?symbol={self._symbol_convert(symbol)}&period={interval}day'
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
                print(f'Huobi public get kline error: {resp["err-msg"]}')
            return lines
        except Exception as e:
            print(f'Huobi public get kline error: {e}')


if __name__ == '__main__':
    huo = HuoPublic('https://api.huobi.pro')
    # print(huo.get_symbol_info('BTC_USDT'))
    # print(huo.get_price('BTC_USDT'))
    # print(huo.get_ticker('BTC_USDT'))
    # print(huo.get_orderbook('BTC_USDT'))
    # print(huo.get_trades('BTC_USDT'))
    print(huo.get_kline('BTC_USDT'))


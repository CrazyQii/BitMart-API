import os
import requests
import time
import math
import json
from datetime import datetime

cur_path = os.path.abspath(os.path.dirname(__file__))


class CoinbenePublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return '/'.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/api/exchange/v2/market/tradePair/list'
            resp = requests.get(url).json()
            if resp['code'] == 200:
                data = {}
                for ticker in resp['data']:
                    data.update({
                        '_'.join(ticker['symbol'].split('/')): {
                            'min_amount': float(ticker['minAmount']),  # 最小下单数量
                            'min_notional': round(math.pow(0.1, float(ticker['pricePrecision'])),
                                                  int(ticker['pricePrecision'])),  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, float(ticker['amountPrecision'])),
                                                      int(ticker['amountPrecision'])),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, float(ticker['pricePrecision'])),
                                                     int(ticker['pricePrecision'])),  # 价格最小变化
                            'amount_digit': int(ticker['amountPrecision']),  # 数量小数位
                            'price_digit': int(ticker['pricePrecision'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Coinbene batch load symbols error')
        except Exception as e:
            print(f'Coinbene batch load symbols exception {e}')

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
            print(f'Bitmart get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = 0.0
            trade = self.get_trades(symbol)
            if len(trade) > 0:
                price = trade[0]['price']
            return price
        except Exception as e:
            print(f'Coinbene public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/api/exchange/v2/market/ticker/one?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            ticker = {}
            if resp['code'] == 200:
                ticker = resp['data']
                ticker = {
                    'symbol': symbol,
                    'last_price': float(ticker['latestPrice']),
                    'quote_volume': None,
                    'base_volume': float(ticker['volume24h']),
                    'highest_price': float(ticker['high24h']),
                    'lowest_price': float(ticker['low24h']),
                    'open_price': None,
                    'close_price': None,
                    'ask_1': float(ticker['bestAsk']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bestBid']),
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['chg24h'].split('%')[0]),
                    'url': url,
                }
            else:
                print(f'Coinbene public get ticker error: {resp}')
            return ticker
        except Exception as e:
            print(f'Coinbene public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/api/exchange/v2/market/orderBook?symbol={symbol}&depth={5}'
            resp = requests.get(url).json()
            orderbook = {'buys': [], 'sells': []}
            if resp['code'] == 200:
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['data']['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': 1
                    })
                for item in resp['data']['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': 1
                    })
            else:
                print(f'Coinbene public get orderbook error: {resp}')
            return orderbook
        except Exception as e:
            print(f'Coinbene public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/api/exchange/v2/market/trades?symbol={self._symbol_convert(symbol)}'
            trades = []
            resp = requests.get(url).json()
            if resp['code'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'amount': float(trade[2]) * float(trade[1]),
                        'order_time': self._utc_to_ts(trade[4]),
                        'price': float(trade[1]),
                        'count': float(trade[2]),
                        'type': trade[3]
                    })
            else:
                print(f'Coinbene public get trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Coinbene public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        end_time = round(time.time())
        start_time = end_time - time_period
        try:
            url = self.urlbase + f'/api/exchange/v2/market/instruments/candles?symbol={self._symbol_convert(symbol)}' \
                                 f'&period={interval}&start={start_time}&end={end_time}'

            resp = requests.get(url).json()
            lines = []
            if resp['code'] == 200:
                for line in resp['data']:
                    lines.append({
                        'timestamp': self._utc_to_ts(line[0]),
                        'open': float(line[1]),
                        'high': float(line[2]),
                        'low': float(line[3]),
                        'volume': float(line[5]),
                        'last_price': float(line[4])
                    })
            else:
                print(f'Coinbene public get kline error: {resp}')
            return lines
        except Exception as e:
            print(f'Coinbene public get kline error: {e}')


if __name__ == '__main__':
    bit = CoinbenePublic('https://openapi-exchange.coinbene.com')
    # print(bit.get_symbol_info('BTC_USDT'))
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    print(bit.get_kline('BTC_USDT'))

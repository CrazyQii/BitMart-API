# -*- coding: utf-8 -*-
"""
okex spot public API
2020/10/14 hlq
"""
import requests
import math
import os
import json
from datetime import datetime, timedelta

cur_path = os.path.abspath(os.path.dirname(__file__))


class OkexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return '-'.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _load_symbols_info(self):
        try:
            url = self.urlbase + 'api/spot/v3/instruments'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                data = {}
                for ticker in resp:
                    data.update({
                        '_'.join(ticker['instrument_id'].split('-')): {
                            'min_amount': float(ticker['min_size']),  # 最小下单数量
                            'min_notional': float(ticker['tick_size']),  # 最小下单金额
                            'amount_increment': float(ticker['size_increment']),  # 数量最小变化
                            'price_increment': float(ticker['tick_size']),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['size_increment'])))),  # 数量小数位
                            'price_digit': int(abs(math.log10(float(ticker['tick_size']))))  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Okex batch load symbols error')
        except Exception as e:
            print(f'Okex batch load symbols exception {e}')

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
            print(f'Okex get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = 0.0
            trade = self.get_trades(symbol)
            if len(trade) > 0:
                price = trade[0]['price']
            return price
        except Exception as e:
            print(f'Okex public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'api/spot/v3/instruments/{self._symbol_convert(symbol)}/ticker'
            resp = requests.get(url)
            ticker = {}
            if resp.status_code == 200:
                resp = resp.json()
                ticker = {
                    'symbol': symbol,
                    'last_price': float(resp['last']),
                    'quote_volume': float(resp['quote_volume_24h']),
                    'base_volume': float(resp['base_volume_24h']),
                    'highest_price': float(resp['high_24h']),
                    'lowest_price': float(resp['low_24h']),
                    'open_price': float(resp['open_24h']),
                    'close_price': float(resp['last']),
                    'ask_1': float(resp['ask']),
                    'ask_1_amount': float(resp['best_ask_size']),
                    'bid_1': float(resp['bid']),
                    'bid_1_amount': float(resp['best_bid_size']),
                    'fluctuation': None,
                    'url': url
                }
            else:
                print(f'Okex public get ticker error: {resp.json()["error_message"]}')
            return ticker
        except Exception as e:
                print(f'Okex public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'api/spot/v3/instruments/{self._symbol_convert(symbol)}/book?size=200&depth=0.2'
            resp = requests.get(url)
            orderbook = {'buys': [], 'sells': []}
            total_amount_buys = 0
            total_amount_sells = 0
            if resp.status_code == 200:
                resp = resp.json()
                for item in resp['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
                for item in resp['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
            else:
                print(f'Okex public get orderbook error: {resp.json()["message"]}')
            return orderbook
        except Exception as e:
            print(f'Okex public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'api/spot/v3/instruments/{self._symbol_convert(symbol)}/trades'
            resp = requests.get(url)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'amount': float(trade['size']) * float(trade['price']),
                        'order_time': self._utc_to_ts(trade['timestamp']),
                        'price': float(trade['price']),
                        'count': float(trade['size']),
                        'type': trade['side']
                    })
            else:
                print(f'Okex public get trades error: {resp.json()["message"]}')
            return trades
        except Exception as e:
            print(f'Okex public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=360, interval=1):
        try:
            end = datetime.utcnow()
            start = end - timedelta(seconds=time_period)
            granularity = int(interval * 60)
            url = self.urlbase + f'api/spot/v3/instruments/{self._symbol_convert(symbol)}/candles?' \
                                 f'granularity={granularity}&start={start.isoformat()}Z&end={end.isoformat()}Z'
            resp = requests.get(url)
            lines = []
            if resp.status_code == 200:
                resp = resp.json()
                for line in resp:
                    lines.append({
                        'timestamp': self._utc_to_ts(line[0]),
                        'open': float(line[1]),
                        'high': float(line[2]),
                        'low': float(line[3]),
                        'volume': float(line[5]),
                        'last_price': float(line[4])
                    })
            else:
                print(f'Okex public get kline error: {resp.json()["message"]}')
            return lines
        except Exception as e:
            print(f'Okex public get kline error: {e}')


if __name__ == "__main__":
    okex = OkexPublic("https://www.okex.com/")
    print(okex.get_symbol_info('BTC_USDT'))
    # print(okex.get_price("BTC_USDT"))
    # print(okex.get_ticker("BTC_USDT"))
    # print(okex.get_orderbook("BTC_USDT"))
    # print(okex.get_trades("BTC_USDT"))
    # print(okex.get_kline("BTC_USDT"))

import requests
import json
import math
import os
from datetime import datetime, timedelta

cur_path = os.path.abspath(os.path.dirname(__file__))


class CoinbasePublic(object):
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
            url = self.urlbase + '/products'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                data = {}
                for ticker in resp:
                    data.update({
                        '_'.join(ticker['id'].split('-')): {
                            'min_amount': float(ticker['base_min_size']),  # 最小下单数量
                            'min_notional': float(ticker['quote_increment']),  # 最小下单金额
                            'amount_increment': float(ticker['base_increment']),  # 数量最小变化
                            'price_increment': float(ticker['quote_increment']),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['base_increment'])))),  # 数量小数位
                            'price_digit': int(abs(math.log10(float(ticker['quote_increment']))))  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Coinbase batch load symbols error')
        except Exception as e:
            print(f'Coinbase batch load symbols exception {e}')

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
            print(f'Coinbase get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = self.get_trades(symbol)
            if price is None:
                return 0.0
            return price
        except Exception as e:
            print(f'Coinbase public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/products/{self._symbol_convert(symbol)}/stats'
            resp_stats = requests.get(url)
            url = self.urlbase + f'/products/{self._symbol_convert(symbol)}/ticker'
            resp_ticker = requests.get(url)
            result = {}
            if resp_stats.status_code == 200 and resp_ticker.status_code == 200:
                ticker = resp_ticker.json()
                stats = resp_stats.json()
                result = {
                    'symbol': symbol,
                    'last_price': float(ticker['price']),
                    'quote_volume': float(ticker['volume']),
                    'base_volume': float(stats['volume']),
                    'highest_price': float(stats['high']),
                    'lowest_price': float(stats['low']),
                    'open_price': float(stats['open']),
                    'close_price': float(stats['last']),
                    'ask_1': float(ticker['ask']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bid']),
                    'bid_1_amount': None,
                    'fluctuation': None,
                    'url': url,
                }
            else:
                print(f'Coinbase public get ticker request error: {resp_stats.json()} and {resp_ticker.json()}')
            return result
        except Exception as e:
            print(f'Coinbase public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/products/{self._symbol_convert(symbol)}/book'
            resp = requests.get(url)
            orderbook = {'buys': [], 'sells': []}
            if resp.status_code == 200:
                resp = resp.json()
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
                for item in resp['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
            else:
                print(f'Coinbase public get orderbook request error: {resp.json()}')
            return orderbook
        except Exception as e:
            print(f'Coinbase public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/products/{self._symbol_convert(symbol)}/trades'
            resp = requests.get(url)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'count': float(trade['size']),
                        'order_time': self._utc_to_ts(trade['time']),
                        'price': float(trade['price']),
                        'amount': float(trade['size']) * float(trade['price']),
                        'type': trade['side']
                    })
                return trades
            else:
                print(f'Coinbase public get trades request error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'Coinbase public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(seconds=time_period)
            url = self.urlbase + f'/products/{self._symbol_convert(symbol)}/candles'
            params = {
                'start': start_time,
                'end': end_time,
                'granularity': interval * 60
            }
            resp = requests.get(url, params=params)
            lines = []
            if resp.status_code == 200:
                resp = resp.json()
                for line in resp:
                    lines.append({
                        'timestamp': line[0],
                        'volume': float(line[5]),
                        'open_price': float(line[3]),
                        'current_price': float(line[4]),
                        'lowest_price': float(line[4]),
                        'highest_price': float(line[2])
                    })
            else:
                print(f'Coinbase public get kline request error: {resp.json()}')
            return lines
        except Exception as e:
            print(f'Coinbase public get kline error: {e}')


if __name__ == '__main__':
    bit = CoinbasePublic('https://api-public.sandbox.pro.coinbase.com')
    # print(bit.get_symbol_info('BTC_USD'))
    # print(bit.get_price('BTC_USD'))
    # print(bit.get_ticker('BTC_USD'))
    # print(bit.get_orderbook('BTC_USD'))
    # print(bit.get_trades('BTC_USD'))
    # print(bit.get_kline('BTC_USD'))
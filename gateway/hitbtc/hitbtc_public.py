import requests
import json
import math
import os
from datetime import datetime
import time

cur_path = os.path.abspath(os.path.dirname(__file__))


class HitbtcPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/api/2/public/symbol'
            resp = requests.get(url)
            if resp.status_code == 200:
                data = {}
                for ticker in resp.json():
                    data.update({
                        f'{ticker["baseCurrency"]}_{ticker["quoteCurrency"]}': {
                            'min_amount': float(ticker['quantityIncrement']),  # 最小下单数量
                            'min_notional': float(ticker['tickSize']),  # 最小下单金额
                            'amount_increment': float(ticker['quantityIncrement']),  # 数量最小变化
                            'price_increment': float(ticker['tickSize']),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['quantityIncrement'])))),  # 数量小数位
                            'price_digit': int(abs(math.log10(float(ticker['tickSize']))))  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Hitbtc batch load symbols error')
        except Exception as e:
            print(f'Hitbtc batch load symbols exception {e}')

    def get_symbol_info(self, symbol: str):
        try:
            symbol_info = dict()
            with open(f'{cur_path}\symbols_detail.json', 'r') as f:
                symbols_detail = json.load(f)
            f.close()

            if symbol not in symbols_detail.keys():
                # update symbols detail
                self._load_symbols_info()

                with open(f'{cur_path}\symbols_detail.json', 'r') as f:
                    symbols_detail = json.load(f)
                f.close()

            symbol_info['symbol'] = symbol
            symbol_info['min_amount'] = symbols_detail[symbol]['min_amount']
            symbol_info['min_notional'] = symbols_detail[symbol]['min_notional']
            symbol_info['amount_increment'] = symbols_detail[symbol]['amount_increment']
            symbol_info['price_increment'] = symbols_detail[symbol]['price_increment']
            symbol_info['amount_digit'] = symbols_detail[symbol]['amount_digit']
            symbol_info['price_digit'] = symbols_detail[symbol]['price_digit']
            return symbol_info
        except Exception as e:
            print(f'Hitbtc get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = self.get_trades(symbol)[0]['price']
            return price if price else 0.0
        except Exception as e:
            print(f'Hitbtc public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/api/2/public/ticker'

            params = {'symbols': self._symbol_convert(symbol)}
            resp = requests.get(url, params=params)
            ticker = {}
            if resp.status_code == 200:
                ticker = resp.json()[0]
                ticker = {
                    'symbol': self._symbol_convert(symbol),
                    'last_price': float(ticker['last']),
                    'quote_volume': float(ticker['volumeQuote']),
                    'base_volume': float(ticker['volume']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': float(ticker['open']),
                    'close_price': float(ticker['last']),
                    'ask_1': float(ticker['ask']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bid']),
                    'bid_1_amount': None,
                    'fluctuation': None,
                    'url': url,
                }
            else:
                print(f'Hitbtc public request error: {resp.json()["error"]}')
            return ticker
        except Exception as e:
            print(f'Hitbtc public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + '/api/2/public/orderbook'
            params = {'symbols': self._symbol_convert(symbol)}

            resp = requests.get(url, params=params)
            orderbook = {'buys': [], 'sells': []}
            total_amount_buys = 0
            total_amount_sells = 0
            if resp.status_code == 200:
                resp = resp.json()
                for item in resp[self._symbol_convert(symbol)]['bid']:
                    total_amount_buys += float(item['size'])
                    orderbook['buys'].append({
                        'amount': float(item['size']),
                        'total': total_amount_buys,
                        'price': float(item['price']),
                        'count': None
                    })
                for item in resp[self._symbol_convert(symbol)]['ask']:
                    total_amount_sells += float(item['size'])
                    orderbook['sells'].append({
                        'amount': float(item['size']),
                        'total': total_amount_sells,
                        'price': float(item['price']),
                        'count': None
                    })
            else:
                print(f'Hitbtc public request error: {resp.json()["error"]}')
            return orderbook
        except Exception as e:
            print(f'Hitbtc public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + '/api/2/public/trades'

            params = {'symbols': self._symbol_convert(symbol)}
            resp = requests.get(url, params=params)
            trades = []
            if resp.status_code == 200:
                for trade in resp.json()[self._symbol_convert(symbol)]:
                    trades.append({
                        'amount': float(trade['quantity']),
                        'order_time': self._utc_to_ts(trade['timestamp']),
                        'price': float(trade['price']),
                        'count': None,
                        'type': trade['side']
                    })
            else:
                print(f'Hitbtc public request error: {resp.json()["error"]}')
            return trades
        except Exception as e:
            print(f'Hitbtc public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            end_time = int(time.time())
            start_time = end_time - time_period
            url = self.urlbase + '/api/2/public/candles'
            params = {
                'symbols': self._symbol_convert(symbol),
                'from': start_time,
                'till': end_time
            }
            resp = requests.get(url, params)
            lines = []
            if resp.status_code == 200:
                resp = resp.json()
                for line in resp[self._symbol_convert(symbol)]:
                    lines.append({
                        'timestamp': self._utc_to_ts(line['timestamp']),
                        'open': float(line['open']),
                        'high': float(line['max']),
                        'low': float(line['min']),
                        'volume': float(line['volume']),
                        'last_price': float(line['close'])
                    })
            else:
                print(f'Hitbtc public request error: {resp.json()["error"]}')
            return lines
        except Exception as e:
            print(f'Hitbtc public get kline error: {e}')


if __name__ == '__main__':
    hit = HitbtcPublic('https://api.hitbtc.com')
    # print(hit.get_symbol_info('BTC_EOSDT'))
    # print(hit.get_price('BTC_EOSDT'))
    # print(hit.get_ticker('BTC_EOSDT'))
    # print(hit.get_orderbook('BTC_EOSDT'))
    # print(hit.get_trades('BTC_EOSDT'))
    # print(hit.get_kline('ETH_BTC'))

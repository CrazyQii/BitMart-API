import requests
import math
import os
import json
import time

cur_path = os.path.abspath(os.path.dirname(__file__))


class MxcPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _uts_to_ts(self, uts):
        timeArray = time.strptime(uts, '%Y-%m-%d %H:%M:%S.%f')
        ts = time.mktime(timeArray)
        return ts

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/open/api/v1/data/markets_info'
            resp = requests.get(url).json()
            if resp['code'] == 200:
                data = {}
                for ticker in resp['data'].items():
                    key = ticker[0]
                    value = ticker[1]
                    data.update({
                        key: {
                            'min_amount': float(value['minAmount']),  # 最小下单数量
                            'min_notional': round(math.pow(0.1, int(value['priceScale'])),
                                                  int(value['priceScale'])),  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, int(value['quantityScale'])),
                                                      int(value['quantityScale'])),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, float(value['priceScale'])),
                                                     int(value['priceScale'])),  # 价格最小变化
                            'amount_digit': int(value['quantityScale']),  # 数量小数位
                            'price_digit': int(value['priceScale'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Mxc batch load symbols error')
        except Exception as e:
            print(f'Mxc batch load symbols exception {e}')

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
            print(f'Mxc get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = 0.0
            trade = self.get_trades(symbol)
            if len(trade) > 0:
                price = trade[0]['price']
            return price
        except Exception as e:
            print(f'Mxc public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/open/api/v1/data/ticker'
            params = {'market': symbol}
            resp = requests.get(url, params=params).json()
            ticker = {}
            if resp['code'] == 200:
                ticker = resp['data']
                ticker = {
                    'symbol': symbol,
                    'last_price': float(ticker['last']),
                    'quote_volume': None,
                    'base_volume': float(ticker['volume']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': float(ticker['open']),
                    'close_price': None,
                    'ask_1': float(ticker['sell']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['buy']),
                    'bid_1_amount': None,
                    'fluctuation': None,
                    'url': url,
                }
            else:
                print(f'Mxc public get ticker error: {resp["msg"]}')
            return ticker
        except Exception as e:
            print(f'Mxc public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + '/open/api/v1/data/depth'
            params = {'market': symbol, 'depth': 20}
            resp = requests.get(url, params=params).json()
            orderbook = {"buys": [], "sells": []}
            if resp['code'] == 200:
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['data']['bids']:
                    total_amount_buys += float(item['quantity'])
                    orderbook['buys'].append({
                        'amount': float(item['quantity']),
                        'total': total_amount_buys,
                        'price': float(item['price']),
                        'count': 1
                    })
                for item in resp['data']['asks']:
                    total_amount_sells += float(item['quantity'])
                    orderbook['sells'].append({
                        'amount': float(item['quantity']),
                        'total': total_amount_buys,
                        'price': float(item['price']),
                        'count': 1
                    })
            else:
                print(f'Mxc public get orderbook error: {resp["msg"]}')
            return orderbook
        except Exception as e:
            print(f'Mxc public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + '/open/api/v1/data/history'
            params = {'market': symbol}
            resp = requests.get(url, params=params).json()
            trades = []
            if resp['code'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'amount': float(trade['tradeQuantity']) * float(trade['tradePrice']),
                        'order_time': round(self._uts_to_ts(trade['tradeTime'])),
                        'price': float(trade['tradePrice']),
                        'count': float(trade['tradeQuantity']),
                        'type': 'buy' if trade['tradeType'] == '1' else 'sell'
                    })
            else:
                print(f'Mxc public get trades error: {resp["msg"]}')
            return trades
        except Exception as e:
            print(f'Mxc public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            url = self.urlbase + '/open/api/v1/data/kline'
            end_time = int(time.time())
            start_time = end_time - time_period
            params = {'market': symbol, 'startTime': start_time, 'interval': f'{interval}m'}

            resp = requests.get(url, params=params).json()
            lines = []
            if resp['code'] == 200:
                for line in resp['data']:
                    lines.append({
                        'timestamp': int(line[0]),
                        'open': float(line[1]),
                        'high': float(line[3]),
                        'low': float(line[4]),
                        'volume': float(line[5]),
                        'last_price': float(line[2])
                    })
            else:
                print(f'Mxc public get kline error: {resp["msg"]}')
            return lines
        except Exception as e:
            print(f'Mxc public get kline error: {e}')


if __name__ == '__main__':
    mxc = MxcPublic('https://www.mxcio.co')
    # print(mxc.get_symbol_info('BTC_USDT'))
    print(mxc.get_price('BTC_USDT'))
    print(mxc.get_ticker('BTC_USDT'))
    print(mxc.get_orderbook('BTC_USDT'))
    print(mxc.get_trades('BTC_USDT'))
    print(mxc.get_kline('BTC_USDT'))

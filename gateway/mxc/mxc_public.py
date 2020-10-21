import requests
import math
import os
import json
import time

cur_path = os.path.abspath(os.path.dirname(__file__))


class MxcPublic(object):
    def __init__(self, urlbase, api_key, api_secret=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/open/api/v2/market/symbols'
            params = {'api_key': self.api_key}
            resp = requests.get(url, params=params).json()
            if resp['code'] == 200:
                data = {}
                for ticker in resp['data']:
                    data.update({
                        ticker['symbol']: {
                            'min_amount': float(ticker['min_amount']),  # 最小下单数量
                            'min_notional': None,  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, int(ticker['quantity_scale'])),
                                                      int(ticker['quantity_scale'])),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, float(ticker['price_scale'])),
                                                     int(ticker['price_scale'])),  # 价格最小变化
                            'amount_digit': int(ticker['quantity_scale']),  # 数量小数位
                            'price_digit': int(ticker['price_scale'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Mxc batch load symbols error')
        except Exception as e:
            print(f'Mxc batch load symbols exception {e}')

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
            print(f'Mxc get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            return self.get_trades(symbol)[0]['price']
        except Exception as e:
            print(f'Mxc public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/open/api/v2/market/ticker'
            params = {'api_key': self.api_key, 'symbol': symbol}
            resp = requests.get(url, params=params).json()
            ticker = {}
            if resp['code'] == 200:
                ticker = resp['data'][0]
                ticker = {
                    'symbol': ticker['symbol'],
                    'last_price': float(ticker['last']),
                    'quote_volume': None,
                    'base_volume': float(ticker['volume']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': float(ticker['open']),
                    'close_price': None,
                    'ask_1': float(ticker['ask']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bid']),
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['change_rate']),
                    'url': url,
                }
            else:
                print(f'Mxc public request error: {resp["msg"]}')
            return ticker
        except Exception as e:
            print(f'Mxc public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + "/open/api/v2/market/depth"
            params = {'api_key': self.api_key, 'symbol': symbol, 'depth': 20}
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
                        'count': None
                    })
                for item in resp['data']['asks']:
                    total_amount_sells += float(item['quantity'])
                    orderbook['sells'].append({
                        'amount': float(item['quantity']),
                        'total': total_amount_buys,
                        'price': float(item['price']),
                        'count': None
                    })
            else:
                print(f'Mxc public request error: {resp["msg"]}')
            return orderbook
        except Exception as e:
            print(f'Mxc public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f"/open/api/v2/market/deals"
            params = {'api_key': self.api_key, 'symbol': symbol}
            resp = requests.get(url, params=params).json()
            trades = []
            if resp['code'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'amount': float(trade['trade_quantity']) * float(trade['trade_price']),
                        'order_time': int(trade['trade_time'] / 1000),
                        'price': float(trade['trade_price']),
                        'count': float(trade['trade_quantity']),
                        'type': 'buy' if trade['trade_type'] == 'BID' else 'sell'
                    })
            else:
                print(f'Mxc public request error: {resp["msg"]}')
            return trades
        except Exception as e:
            print(f'Mxc public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            url = self.urlbase + '/open/api/v2/market/kline'
            end_time = int(time.time())
            start_time = end_time - time_period
            params = {'api_key': self.api_key, 'symbol': symbol, 'start_time': start_time, 'interval': interval}

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
                print(f'Mxc public request error: {resp["msg"]}')
            return lines
        except Exception as e:
            print(f'Mxc public get kline error: {e}')


if __name__ == '__main__':
    mxc = MxcPublic('https://www.mxcio.co', 'mx0Iw5GHIlySTepTAN', 'ec4f09f088d642d2b2ebfae695b9c511')
    # print(mxc.get_symbol_info('BTC_USDT'))
    # print(mxc.get_price('BTC_USDT'))
    # print(mxc.get_ticker('BTC_USDT'))
    # print(mxc.get_orderbook('BTC_USDT'))
    # print(mxc.get_trades('BTC_USDT'))
    # print(mxc.get_kline('BTC_USDT'))

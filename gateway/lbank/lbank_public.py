import os
import json
import requests
import math
import time

cur_path = os.path.abspath(os.path.dirname(__file__))


class LbankPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_conver(self, symbol: str):
        return symbol.lower()

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/accuracy.do'
            resp = requests.get(url).json()
            if resp['result']:
                data = {}
                for ticker in resp['data']:
                    data.update({
                        ticker['symbol'].upper(): {
                            'min_amount': round(math.pow(0.1, float(ticker['quantityAccuracy'])),
                                                int(ticker['quantityAccuracy'])),  # 最小下单数量
                            'min_notional': round(math.pow(0.1, float(ticker['priceAccuracy'])),
                                                  int(ticker['priceAccuracy'])),  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, float(ticker['quantityAccuracy'])),
                                                      int(ticker['quantityAccuracy'])),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, float(ticker['priceAccuracy'])),
                                                     int(ticker['priceAccuracy'])),  # 价格最小变化
                            'amount_digit': int((ticker['quantityAccuracy'])),  # 数量小数位
                            'price_digit': int(ticker['priceAccuracy'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Lbank batch load symbols error')
        except Exception as e:
            print(f'Lbank batch load symbols exception {e}')

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
            print(f'Lbank get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = self.get_trades(symbol)[0]
            if price:
                return price
            else:
                return 0.0
        except Exception as e:
            print(e)

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/ticker.do'
            params = {'symbol': self._symbol_conver(symbol)}
            resp = requests.get(url, params=params).json()
            ticker = {}
            if resp['result']:
                ticker = resp['data'][0]['ticker']
                ticker = {
                    'symbol': symbol,
                    'last_price': float(ticker['latest']),
                    'quote_volume': None,
                    'base_volume': float(ticker['vol']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': float(ticker['latest']),
                    'close_price': None,
                    'ask_1': None,
                    'ask_1_amount': None,
                    'bid_1': None,
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['change']),
                    'url': url,
                }
            else:
                print(f'Lbank public request error: {resp["data"]}')
            return ticker
        except Exception as e:
            print(f'Lbank public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + '/incrDepth.do'
            params = {
                'symbol': self._symbol_conver(symbol)
            }
            resp = requests.get(url, params=params).json()
            orderbook = {'buys': [], 'sells': []}
            total_amount_buys = 0
            total_amount_sells = 0
            if resp['result']:
                for item in resp['data']['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': None
                    })
                for item in resp['data']['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': None
                    })
            else:
                print(f'Lbank public request error: {resp["data"]}')
            return orderbook
        except Exception as e:
            print(f'Lbank public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/trades.do'
            params = {
                'symbol': self._symbol_conver(symbol),
                'size': 100
            }
            trades = []
            resp = requests.get(url, params=params).json()
            if resp['result']:
                for trade in resp['data']:
                    trades.append({
                        'amount': float(trade['amount']),
                        'order_time': round(trade['date_ms'] / 1000),
                        'price': float(trade['price']),
                        'count': None,
                        'type': trade['type']
                    })
            else:
                print(f'Lbank public request error: {resp["data"]}')
            return trades
        except Exception as e:
            print(f'Lbank public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        end_time = round(time.time())
        start_time = end_time - time_period
        try:
            url = self.urlbase + '/kline.do'
            params = {
                'symbol': self._symbol_conver(symbol),
                'size': 100,
                'type': f'minute{interval}',
                'time': start_time
            }

            resp = requests.get(url, params=params).json()
            print(resp)
            lines = []
            if resp['result']:
                for line in resp['data']:
                    lines.append({
                        'timestamp': line[0],
                        'open': float(line[1]),
                        'high': float(line[2]),
                        'low': float(line[3]),
                        'volume': float(line[5]),
                        'last_price': float(line[4])
                    })
            else:
                print(f'Lbank public request error: {resp["data"]}')
            return lines
        except Exception as e:
            print(f'Lbank public get kline error: {e}')


if __name__ == '__main__':
    bit = LbankPublic('https://www.lbkex.net/v2')
    # print(bit.get_symbol_info('BTC_USDT'))
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))

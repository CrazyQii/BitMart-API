import requests
import math
import json
import os
import time

cur_path = os.path.abspath(os.path.dirname(__file__))


class GateioPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/spot/currency_pairs'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                data = {}
                for ticker in resp:
                    data.update({
                        ticker['id']: {
                            'min_amount': float(ticker['min_base_amount']) if ticker['min_base_amount'] else None,  # 最小下单数量
                            'min_notional': float(ticker['min_quote_amount']) if ticker['min_quote_amount'] else None,  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, int(ticker['amount_precision'])), int(ticker['amount_precision'])),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, int(ticker['precision'])), int(ticker['precision'])),  # 价格最小变化
                            'amount_digit': int(ticker['amount_precision']),  # 数量小数位
                            'price_digit': int(ticker['precision'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Gateio batch load symbols error')
        except Exception as e:
            print(f'Gateio batch load symbols exception {e}')

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
            print(f'Gateio get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/tickers?currency_pair={symbol}'
            resp = requests.get(url)
            price = 0.0
            if resp.status_code == 200:
                price = float(resp.json()[0]["last"])
            else:
                print(f'Gateio public get price request error: {resp.json()}')
            return price
        except Exception as e:
            print(f'Gateio public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/tickers?currency_pair={symbol}'
            resp = requests.get(url)
            ticker = {}
            if resp.status_code == 200:
                ticker = resp.json()[0]
                ticker = {
                    'symbol': ticker['currency_pair'],
                    'last_price': float(ticker['last']),
                    'quote_volume': float(ticker['quote_volume']),
                    'base_volume': float(ticker['base_volume']),
                    'highest_price': float(ticker['high_24h']),
                    'lowest_price': float(ticker['low_24h']),
                    'open_price': None,
                    'close_price': None,
                    'ask_1': float(ticker['lowest_ask']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['highest_bid']),
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['change_percentage']),
                    'url': url,
                }
            else:
                print(f'Gateio public get ticker request error: {resp.json()}')
            return ticker
        except Exception as e:
            print(f'Gateio public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/order_book?currency_pair={symbol}&limit=20'
            resp = requests.get(url)
            orderbook = {'buys': [], 'sells': []}
            if resp.status_code == 200:
                resp = resp.json()
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': 1
                    })
                for item in resp['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': 1
                    })
            else:
                print(f'Gateio public get orderbook request error: {resp.json()}')
            return orderbook
        except Exception as e:
            print(f'Gateio public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/spot/trades?currency_pair={symbol}&limit=40'
            resp = requests.get(url)
            trades = []
            if resp.status_code == 200:
                for trade in resp.json():
                    trades.append({
                        'amount': float(trade['amount']) * float(trade['price']),
                        'order_time': int(trade['create_time']),
                        'price': float(trade['price']),
                        'count': float(trade['amount']),
                        'type': trade['side']
                    })
            else:
                print(f'Gateio public get trades request error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'Gateio public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            end_time = int(time.time())
            start_time = end_time - time_period
            url = self.urlbase + f'/spot/candlesticks?currency_pair={symbol}&from={start_time}&to={end_time}&interval={interval}m'

            resp = requests.get(url)
            lines = []
            if resp.status_code == 200:
                for line in resp.json():
                    lines.append({
                        'timestamp': int(line[0]),
                        'open': float(line[5]),
                        'high': float(line[3]),
                        'low': float(line[4]),
                        'volume': float(line[1]),
                        'last_price': float(line[2])
                    })
            else:
                print(f'Gateio public get kline request error: {resp.json()}')
            return lines
        except Exception as e:
            print(f'Gateio public get kline error: {e}')


if __name__ == '__main__':
    gate = GateioPublic('https://api.gateio.ws/api/v4')
    # print(gate.get_symbol_info('BTC_USDT'))
    print(gate.get_price('BTC_USDT'))
    print(gate.get_ticker('BTC_USDT'))
    print(gate.get_orderbook('BTC_USDT'))
    print(gate.get_trades('BTC_USDT'))
    print(gate.get_kline('BTC_USDT'))

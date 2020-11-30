import os
import math
import json
import requests
import time

cur_path = os.path.abspath(os.path.dirname(__file__))


class VinexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_symbols_info(self):
        """ initialize symbol details in json """
        try:
            url = self.urlbase + '/api/v2/markets'
            resp = requests.get(url).json()
            if resp['status'] == 200:
                data = {}
                for ticker in resp['data']:
                    data.update({
                        ticker['symbol']: {
                            'min_amount': round(math.pow(0.1, float(ticker['decAmount'])),
                                                int(ticker['decAmount'])),  # 最小下单数量
                            'min_notional': round(math.pow(0.1, float(ticker['decPrice'])),
                                                  int(ticker['decPrice'])),  # 最小下单金额
                            'amount_increment': round(math.pow(0.1, float(ticker['decAmount'])),
                                                      int(ticker['decAmount'])),  # 价格最小变化
                            'price_increment': round(math.pow(0.1, float(ticker['decPrice'])),
                                                     int(ticker['decPrice'])),  # 价格最小变化
                            'amount_digit': int(ticker['decAmount']),  # 数量小数位
                            'price_digit': int(ticker['decPrice'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Vinex batch load symbols error')
        except Exception as e:
            print(f'Vinex batch load symbols exception {e}')

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
            trade = self.get_trades(symbol)[0]
            if trade is not None:
                price = trade['price']
            return price
        except Exception as e:
            print(f'Vinex public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v2/get-ticker?market={symbol}'
            resp = requests.get(url).json()
            ticker = {}
            if resp['status'] == 200:
                ticker = resp['data']
                ticker = {
                    'symbol': symbol,
                    'last_price': float(ticker['lastPrice']),
                    'quote_volume': float(ticker['quoteVolume']),
                    'base_volume': float(ticker['baseVolume']),
                    'highest_price': float(ticker['highPrice']),
                    'lowest_price': float(ticker['lowPrice']),
                    'open_price': None,
                    'close_price': None,
                    'ask_1': float(ticker['askPrice']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bidPrice']),
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['change24h']),
                    'url': url,
                }
            else:
                print(f'Vinex public get ticker request error: {resp}')
            return ticker
        except Exception as e:
            print(f'Vinex public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v2/get-order-book?market={symbol}'
            resp = requests.get(url).json()
            print(resp)
            orderbook = {'buys': [], 'sells': []}
            total_amount_buys = 0
            total_amount_sells = 0
            if resp['status'] == 200:
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
                        'total': total_amount_sells,
                        'price': float(item['price']),
                        'count': None
                    })
            else:
                print(f'Vinex public get orderbook request error: {resp}')
            return orderbook
        except Exception as e:
            print(f'Vinex public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/api/v2/get-market-history?market={symbol}'
            trades = []
            resp = requests.get(url).json()
            if resp['status'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'amount': float(trade['amount']) * int(trade['amount']),
                        'order_time': int(trade['createdAt']),
                        'price': float(trade['price']),
                        'count': float(trade['amount']),
                        'type': 'buy' if trade['type'] == 1 else 'sell'
                    })
            else:
                print(f'Vinex public get trades request error: {resp}')
            return trades
        except Exception as e:
            print(f'Vinex public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        endTime = round(time.time())
        startTime = endTime - time_period
        try:
            url = self.urlbase + f'/api/v2/candles?symbol={symbol}&interval={interval}m&from={startTime}&to={endTime}'

            resp = requests.get(url).json()
            lines = []
            print(resp)
            if resp['status'] == 200:
                for line in resp['data']:
                    lines.append({
                        'timestamp': int(line['timestamp']),
                        'open': float(line['open']),
                        'high': float(line['high'])
                    })
            else:
                print(f'Vinex public get kline request error: {resp}')
            return lines
        except Exception as e:
            print(f'Vinex public get kline error: {e}')


if __name__ == '__main__':
    bit = VinexPublic('https://api.vinex.network')
    # print(bit.get_symbol_info('BTC_ETH'))
    # print(bit.get_price('BTC_ETH'))
    # print(bit.get_ticker('BTC_ETH'))
    # print(bit.get_orderbook('BTC_ETH'))
    # print(bit.get_trades('BTC_ETH'))
    # print(bit.get_kline('BTC_ETH'))
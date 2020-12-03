import os
import requests
import time
import math
import json

cur_path = os.path.abspath(os.path.dirname(__file__))


class ZGPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return ''.join(symbol.split('_'))

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/openapi/v1/brokerInfo'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                data = {}
                for ticker in resp['symbols']:
                    data.update({
                        f"{ticker['baseAsset']}_{ticker['quoteAsset']}": {
                            'min_amount': float(ticker['baseAssetPrecision']),  # 最小下单数量
                            'min_notional': float(ticker['filters'][2]['minNotional']),  # 最小下单金额
                            'amount_increment': float(ticker['filters'][1]['stepSize']),  # 数量最小变化
                            'price_increment': float(ticker['filters'][0]['tickSize']),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['filters'][1]['minQty'])))),  # 数量小数位
                            'price_digit': int(abs(math.log10(float(ticker['filters'][0]['minPrice']))))  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('ZG batch load symbols error')
        except Exception as e:
            print(f'ZG batch load symbols exception {e}')

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
            print(f'ZG get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            url = self.urlbase + f'/openapi/quote/v1/ticker/price?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            price = 0.0
            if 'code' not in resp:
                price = resp['price']
            else:
                print(f'ZG public get price error: {resp["msg"]}')
            return price
        except Exception as e:
            print(f'ZG public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/openapi/quote/v1/ticker/24hr?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            ticker = {}
            if 'code' not in resp:
                ticker = resp
                ticker = {
                    'symbol': symbol,
                    'last_price': float(ticker['lastPrice']),
                    'quote_volume': float(ticker['quoteVolume']),
                    'base_volume': float(ticker['volume']),
                    'highest_price': float(ticker['highPrice']),
                    'lowest_price': float(ticker['lowPrice']),
                    'open_price': float(ticker['openPrice']),
                    'close_price': None,
                    'ask_1': float(ticker['bestAskPrice']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bestBidPrice']),
                    'bid_1_amount': None,
                    'fluctuation': None,
                    'url': url,
                }
            else:
                print(f'ZG public get ticker error: {resp["msg"]}')
            return ticker
        except Exception as e:
            print(f'ZG public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/openapi/quote/v1/depth?symbol={self._symbol_convert(symbol)}'
            resp = requests.get(url).json()
            orderbook = {'buys': [], 'sells': []}
            if 'code' not in resp:
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': 1
                    })
                for item in resp['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': 1
                    })
            else:
                print(f'ZG public get orderbook error: {resp["msg"]}')
            return orderbook
        except Exception as e:
            print(f'ZG public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/openapi/quote/v1/trades?symbol={self._symbol_convert(symbol)}'
            trades = []
            resp = requests.get(url).json()
            if 'code' not in resp:
                for trade in resp:
                    trades.append({
                        'amount': float(trade['qty']) * float(trade['price']),
                        'order_time': round(trade['time'] / 1000),
                        'price': float(trade['price']),
                        'count': float(trade['qty']),
                        'type': 'buy' if trade['isBuyerMaker'] else 'sell'
                    })
            else:
                print(f'ZG public get trades error: {resp["msg"]}')
            return trades
        except Exception as e:
            print(f'ZG public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        end_time = round(time.time())
        start_time = end_time - time_period
        try:
            url = self.urlbase + f'/openapi/quote/v1/klines?symbol={self._symbol_convert(symbol)}&interval={interval}m' \
                                 f'&startTime={start_time}&endTime={end_time}'

            resp = requests.get(url).json()
            lines = []
            if 'code' not in resp:
                for line in resp:
                    lines.append({
                        'timestamp': line[6],
                        'open': float(line[1]),
                        'high': float(line[2]),
                        'low': float(line[3]),
                        'volume': float(line[5]),
                        'last_price': float(line[4])
                    })
            else:
                print(f'ZG public get kline error: {resp["msg"]}')
            return lines
        except Exception as e:
            print(f'ZG public get kline error: {e}')


if __name__ == '__main__':
    bit = ZGPublic('https://api.zg6.com')
    print(bit.get_symbol_info('BTC_USDT'))
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))
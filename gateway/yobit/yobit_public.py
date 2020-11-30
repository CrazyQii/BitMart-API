import os
import requests
import math
import json

cur_path = os.path.abspath(os.path.dirname(__file__))


class YoubitPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/info'
            resp = requests.get(url)
            if resp.status_code == 200:
                data = {}
                resp = resp.json()
                for ticker in resp['pairs'].keys():
                    data.update({
                        ticker.upper(): {
                            'min_amount': float(resp['pairs'][ticker]['min_amount']),  # 最小下单数量
                            'min_notional': float(resp['pairs'][ticker]['min_price']),  # 最小下单金额
                            'amount_increment': float(resp['pairs'][ticker]['min_amount']),  # 数量最小变化
                            'price_increment': float(resp['pairs'][ticker]['min_price']),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(resp['pairs'][ticker]['min_amount'])))),  # 数量小数位
                            'price_digit': int(resp['pairs'][ticker]['decimal_places'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Yobit batch load symbols error')
        except Exception as e:
            print(f'Yobit batch load symbols exception {e}')

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
            print(f'Yobit get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = 0.0
            if len(self.get_trades(symbol)) != 0:
                price = self.get_trades(symbol)[0]['price']
            return price
        except Exception as e:
            print(f'Yobit public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/ticker/{symbol.lower()}'
            resp = requests.get(url)
            ticker = {}
            if resp.status_code == 200:
                resp = resp.json()
                key = ''
                for key in resp.keys():
                    key = key
                ticker = resp[key]
                ticker = {
                    'symbol': key.upper(),
                    'last_price': float(ticker['last']),
                    'quote_volume': float(ticker['vol_cur']),
                    'base_volume': float(ticker['vol']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': None,
                    'close_price': float(ticker['last']),
                    'ask_1': float(ticker['sell']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['buy']),
                    'bid_1_amount': None,
                    'fluctuation': None,
                    'url': url,
                }
            else:
                print(f'Yobit public get ticker request error: {resp.json()}')
            return ticker
        except Exception as e:
            print(f'Yobit public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/depth/{symbol.lower()}'
            resp = requests.get(url)
            orderbook = {'buys': [], 'sells': []}
            if resp.status_code == 200:
                resp = resp.json()
                key = ''
                for key in resp.keys():
                    key = key
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp[key]['asks']:
                    total_amount_sells += float(item[1])
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': total_amount_sells,
                        'price': float(item[0]),
                        'count': None
                    })
                for item in resp[key]['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': None
                    })
            else:
                print(f'Yobit public get orderbook request error: {resp.json()}')
            return orderbook
        except Exception as e:
            print(f'Yobit public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/trades/{symbol.lower()}'
            trades = []
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                key = ''
                for key in resp.keys():
                    key = key
                for trade in resp[key]:
                    trades.append({
                        'amount': float(trade['amount']),
                        'order_time': round(trade['timestamp']),
                        'price': float(trade['price']),
                        'count': None,
                        'type': 'sell' if trade['type'] == 'ask' else 'buy'
                    })
            else:
                print(f'Yobit public get trades request error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'Yobit public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        pass


if __name__ == '__main__':
    bit = YoubitPublic('https://yobit.net/api/3')
    # print(bit.get_symbol_info('BTC_USDT'))
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    # print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))

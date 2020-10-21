import requests
import json
import os
import math

cur_path = os.path.abspath(os.path.dirname(__file__))


class BiboxPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _handle_limitation(self, limitation, ticker):
        """ 匹配对应交易对限制信息 """
        min_amount = limitation['min_trade_amount']['default']  # 最小下单数量

        min_trade_money = limitation['min_trade_money']  # 最小下单金额

        symbol = ticker.split('_')[1]
        if symbol in min_trade_money.keys():
            min_notional = min_trade_money[symbol]
            return {
                'min_amount': min_amount,
                'min_notional': min_notional,
                'amount_digit': int(abs(math.log10(float(min_amount)))),
                'amount_increment': min_amount
            }
        else:
            return {
                'min_amount': min_amount,
                'min_notional': None,
                'amount_digit': int(abs(math.log10(float(min_amount)))),
                'amount_increment': min_amount
            }

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/v1/orderpending?cmd=tradeLimit'
            resp = requests.get(url)
            if resp.status_code == 200:
                limitation = resp.json()['result']
            else:
                print('Bitmart batch load symbols error')
                return None

            url = self.urlbase + '/v1/mdata?cmd=pairList'
            resp = requests.get(url)
            data = {}
            if resp.status_code == 200:
                for ticker in resp.json()['result']:
                    limit = self._handle_limitation(limitation, ticker['pair'])
                    data.update({
                        ticker['pair']: {
                            'min_amount': limit['min_amount'],
                            'min_notional': limit['min_notional'],
                            'amount_increment': limit['amount_increment'],
                            'price_increment': round(math.pow(0.1, float(ticker['decimal'])),
                                                     int(ticker['decimal'])),  # 价格最小变化
                            'amount_digit': limit['amount_digit'],
                            'price_digit': int(ticker['decimal'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Bibox batch load symbols error')
        except Exception as e:
            print(f'Bibox batch load symbols exception {e}')

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
            print(f'Bibox get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            return self.get_trades(symbol)[0]['price']
        except Exception as e:
            print(f'Bibox public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f'/v1/mdata?cmd=ticker&pair={symbol}'

            resp = requests.get(url)
            ticker = {}
            if resp.status_code == 200:
                ticker = resp.json()['result']
                ticker = {
                    'symbol': ticker['pair'],
                    'last_price': float(ticker['last']),
                    'quote_volume': None,
                    'base_volume': float(ticker['vol']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': None,
                    'close_price': None,
                    'ask_1': float(ticker['sell']),
                    'ask_1_amount': float(ticker['sell_amount']),
                    'bid_1': float(ticker['buy']),
                    'bid_1_amount': float(ticker['buy_amount']),
                    'fluctuation': float(ticker['percent'][1:-1]) / 100,
                    'url': url
                }
            else:
                print(f'Bibox public request error: {resp.json()["error"]["msg"]}')
            return ticker
        except Exception as e:
            print(f'Bibox public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f'/v1/mdata?cmd=depth&pair={symbol}'
            resp = requests.get(url)
            orderbook = {'buys': [], 'sells': []}
            if resp.status_code == 200:
                resp = resp.json()
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['result']['bids']:
                    total_amount_buys += float(item['volume'])
                    orderbook['buys'].append({
                        'amount': float(item['volume']),
                        'total': total_amount_buys,
                        'price': float(item['price']),
                        'count': None
                    })
                for item in resp['result']['asks']:
                    total_amount_sells += float(item['volume'])
                    orderbook['sells'].append({
                        'amount': float(item['volume']),
                        'total': total_amount_sells,
                        'price': float(item['price']),
                        'count': None
                    })
            else:
                print(f'Bibox public request error: {resp.json()["error"]["msg"]}')
            return orderbook
        except Exception as e:
            print(f'Bibox public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/v1/mdata?cmd=deals&pair={symbol}'

            resp = requests.get(url)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp['result']:
                    trades.append({
                        'amount': float(trade['amount']),
                        'order_time': round(trade['time'] / 1000),
                        'price': float(trade['price']),
                        'count': None,
                        'type': 'buy' if trade['side'] == 1 else 'sell'
                    })
            else:
                print(f'Bibox public request error: {resp.json()["error"]["msg"]}')
            return trades
        except Exception as e:
            print(f'Bibox public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=60, interval=1):
        try:
            time_period = int(time_period/60)
            url = self.urlbase + f'/v1/mdata?cmd=kline&pair={symbol}&period={time_period}min'

            resp = requests.get(url)
            lines = []
            if resp.status_code == 200:
                for line in resp.json()['result']:
                    lines.append({
                        'timestamp': int(line['time'] / 1000),
                        'open': float(line['open']),
                        'high': float(line['high']),
                        'low': float(line['low']),
                        'volume': float(line['vol']),
                        'last_price': float(line['close'])
                    })
            else:
                print(f'Bibox public request error: {resp.json()["error"]["msg"]}')
            return lines
        except Exception as e:
            print(f'Bibox public get kline error: {e}')


if __name__ == '__main__':
    bibox = BiboxPublic('https://api.bibox.com')
    # print(bibox.get_symbol_info('BTC_USDT'))
    # print(bibox.get_price('BTC_USDT'))
    # print(bibox.get_ticker('BTC_USDT'))
    # print(bibox.get_orderbook('BTC_USDT'))
    # print(bibox.get_trades('BTC_USDT'))
    # print(bibox.get_kline('BTC_USDT'))
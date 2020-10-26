import requests
import json
import time
import os

cur_path = os.path.abspath(os.path.dirname(__file__))


class XtPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return symbol.lower()

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/data/api/v1/getMarketConfig'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                data = {}
                for ticker_key, ticker_value in resp.items():
                    data.update({
                        ticker_key.upper(): {
                            'min_amount': float(ticker_value['minAmount']),  # 最小下单数量
                            'min_notional': round(pow(0.1, ticker_value['pricePoint']), ticker_value['pricePoint']),  # 最小下单金额
                            'amount_increment': round(pow(0.1, ticker_value['coinPoint']), ticker_value['coinPoint']),  # 数量最小变化
                            'price_increment': round(pow(0.1, ticker_value['pricePoint']), ticker_value['pricePoint']),  # 价格最小变化
                            'amount_digit': int(ticker_value['coinPoint']),  # 数量小数位
                            'price_digit': int(ticker_value['pricePoint'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Xt batch load symbols error')
        except Exception as e:
            print(f'Xt batch load symbols exception {e}')

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
            print(f'Xt get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            price = self.get_trades(symbol)[0]['price']
            if price is None:
                return 0.0
            return price
        except Exception as e:
            print(f'Xt public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + '/data/api/v1/getTicker'
            params = {'market': self._symbol_convert(symbol)}
            resp = requests.get(url, params=params)
            result = {}
            if resp.status_code == 200:
                ticker = resp.json()
                result = {
                    'symbol': symbol,
                    'last_price': float(ticker['price']),
                    'quote_volume': float(ticker['moneyVol']),
                    'base_volume': float(ticker['coinVol']),
                    'highest_price': float(ticker['high']),
                    'lowest_price': float(ticker['low']),
                    'open_price': None,
                    'close_price': float(ticker['price']),
                    'ask_1': float(ticker['ask']),
                    'ask_1_amount': None,
                    'bid_1': float(ticker['bid']),
                    'bid_1_amount': None,
                    'fluctuation': float(ticker['rate']),
                    'url': url,
                }
            else:
                print(f'Xt public request error: {resp.json()}')
            return result
        except Exception as e:
            print(f'Xt public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + '/data/api/v1/getDepth'
            params = {'market': self._symbol_convert(symbol)}
            resp = requests.get(url, params=params)
            orderbook = {
                'buys': [],
                'sells': []
            }
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
                        'count': None
                    })
                for item in resp['bids']:
                    total_amount_buys += float(item[1])
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': total_amount_buys,
                        'price': float(item[0]),
                        'count': None
                    })
            else:
                print(f'Xt public request error: {resp.json()}')
            return orderbook
        except Exception as e:
            print(f'Xt public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + '/data/api/v1/getTrades'
            params = {'market': self._symbol_convert(symbol)}
            resp = requests.get(url, params=params)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        'count': float(trade[2]),
                        'order_time': round(trade[0] / 1000),
                        'price': float(trade[1]),
                        'amount': float(trade[1]) * float(trade[2]),
                        'type': trade[3]
                    })
                return trades
            else:
                print(f'Xt public request error: {resp.json()}')
            return trades
        except Exception as e:
            print(f'Xt public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            end_time = round(time.time())
            start_time = end_time - time_period
            url = self.urlbase + '/data/api/v1/getKLine'
            params = {'market': self._symbol_convert(symbol), 'type': f'{interval}min'}
            resp = requests.get(url, params=params)
            lines = []
            if resp.status_code == 200:
                resp = resp.json()
                for line in resp['datas']:
                    lines.append({
                        'timestamp': line[0],
                        'volume': float(line[5]),
                        'open_price': float(line[1]),
                        'current_price': float(line[4]),
                        'lowest_price': float(line[3]),
                        'highest_price': float(line[2])
                    })
            else:
                print(f'Xt public request error: {resp.json()}')
            return lines
        except Exception as e:
            print(f'Xt public get kline error: {e}')


if __name__ == '__main__':
    bit = XtPublic('https://api.xt.com')
    # print(bit.get_symbol_info('BTC_USDT'))
    # print(bit.get_price('BNA_USDT'))
    # print(bit.get_ticker('BNA_USDT'))
    # print(bit.get_orderbook('BNA_USDT'))
    # print(bit.get_trades('BNA_USDT'))
    # print(bit.get_kline('BNA_USDT'))
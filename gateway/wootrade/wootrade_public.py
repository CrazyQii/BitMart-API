import requests
import os
import math
import json
import time
import hmac
import hashlib

cur_path = os.path.abspath(os.path.dirname(__file__))


class Wootrade(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _symbol_convert(self, symbol):
        return "SPOT_" + symbol

    def _sign_message(self, data):
        try:
            return hmac.new(self.api_secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        except Exception as e:
            print(e)

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/v1/public/info'
            resp = requests.get(url).json()
            if resp['success'] is True:
                data = {}
                for ticker in resp['rows']:
                    symbol = ticker['symbol'].split('_')[1] + '_' + ticker['symbol'].split('_')[2]
                    data.update({
                        symbol: {
                            'min_amount': float(ticker['base_min']),  # 最小下单数量
                            'min_notional': float(ticker['quote_min']),  # 最小下单金额
                            'amount_increment': float(ticker['base_tick']),  # 数量最小变化
                            'price_increment': float(ticker['quote_tick']),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['base_tick'])))),  # 数量小数位
                            'price_digit': int(abs(math.log10(float(ticker['quote_tick']))))  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Wootrade batch load symbols error')
        except Exception as e:
            print(f'Wootrade batch load symbols exception {e}')

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
            print(f'Wootrade get symbol info error: {e}')

    def get_price(self, symbol: str):
        try:
            last_trade = self.get_trades(symbol, 1)
            return last_trade[0]["price"]
        except Exception as e:
            print(f'Wootrade public get price error: {e}')

    # ticker not supported
    def get_ticker(self, symbol: str):
        pass

    def get_orderbook(self, symbol: str):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/v1/orderbook/{symbol}?max_level={30}'

            ts = str(time.time())
            msg = "max_level=30|" + str(ts)
            sign = self._sign_message(msg)

            headers = {"Content-Type": "application/x-www-form-urlencoded",
                      "x-api-key": self.api_key,
                      "x-api-signature": sign,
                      "x-api-timestamp": ts,
                      "cache-control": "no-cache"}

            resp = requests.get(url, headers=headers).json()
            orderbook = {'buys': [], 'sells': []}
            if resp['success'] is True:
                total_amount_buys = 0
                total_amount_sells = 0
                for item in resp['bids']:
                    total_amount_buys += float(item['quantity'])
                    orderbook['buys'].append({
                        'amount': float(item['quantity']),
                        'total': total_amount_buys,
                        'price': float(item['price']),
                        'count': None
                    })
                for item in resp['asks']:
                    total_amount_sells += float(item['total'])
                    orderbook['sells'].append({
                        'amount': float(item['amount']),
                        'total': total_amount_sells,
                        'price': float(item['price']),
                        'count': None
                    })
            else:
                print(f'Wootrade public request error: {resp["message"]}')
            return orderbook
        except Exception as e:
            print(f'Wootrade public get orderbook error: {e}')

    def get_trades(self, symbol: str, limit=10):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/v1/public/market_trades?symbol={symbol}&limit={limit}'
            resp = requests.get(url).json()
            trades = []
            if resp['success'] is True:
                for trade in resp['rows']:
                    trades.append({
                        'amount': float(trade['executed_quantity']) * float(trade['executed_price']),
                        'order_time': int(float(trade['executed_timestamp'])),
                        'price': float(trade['executed_price']),
                        'count': float(trade['executed_quantity']),
                        'type': trade['side'].lower()
                    })
            else:
                print(f'Wootrade public request error: {resp["message"]}')
            return trades
        except Exception as e:
            print(f'Wootrade public get trades error: {e}')

    # kline not supported
    def get_kline(self, symbol: str, time_period=3000, interval=1):
        pass


if __name__ == '__main__':
    woo = Wootrade('https://nexus.kronostoken.com', 'AbmyVJGUpN064ks5ELjLfA==', 'QHKRXHPAW1MC9YGZMAT8YDJG2HPR')
    # print(woo.get_symbol_info('BTC_USDT'))
    # print(woo.get_price('BTC_USDT'))
    # print(woo.get_ticker('BTC_USDT'))
    print(woo.get_orderbook('BTC_USDT'))
    # print(woo.get_trades('BTC_USDT'))
    # print(woo.get_kline('BTC_USDT'))
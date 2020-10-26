import os
from gateway.kucoin.kucoin_python_sdk.kucoin.client import Market
import math
import json

cur_path = os.path.abspath(os.path.dirname(__file__))


class KucoinPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase
        self.market = Market()

    def _symbol_convert(self, symbol: str):
        return '-'.join(symbol.split('_'))

    def _load_symbols_info(self):
        try:
            tickers = self.market.get_symbol_list()
            data = {}
            for ticker in tickers:
                data.update({
                    '_'.join(ticker['symbol'].split('-')): {
                        'min_amount': float(ticker['baseMinSize']),  # 最小下单数量
                        'min_notional': float(ticker['priceIncrement']),  # 最小下单金额
                        'amount_increment': float(ticker['baseIncrement']),  # 数量最小变化
                        'price_increment': float(ticker['priceIncrement']),  # 价格最小变化
                        'amount_digit': int(abs(math.log10(float(ticker['baseIncrement'])))),  # 数量小数位
                        'price_digit': int(abs(math.log10(float(ticker['priceIncrement']))))  # 价格小数位
                    }
                })
                with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
        except Exception as e:
            print(f'Kucoin batch load symbols exception {e}')

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
            print(f'Kucoin get symbol info error: {e}')

    def get_price(self, symbol: str):
        pass

    def get_ticker(self, symbol: str):
        try:
            ticker = self.market.get_24h_stats(self._symbol_convert(symbol))
            ticker = {
                'symbol': symbol,
                'last_price': float(ticker['last']),
                'quote_volume': float(ticker['volValue']),
                'base_volume': float(ticker['vol']),
                'highest_price': float(ticker['high']),
                'lowest_price': float(ticker['low']),
                'open_price': None,
                'close_price': float(ticker['last']),
                'ask_1': float(ticker['sell']),
                'ask_1_amount': None,
                'bid_1': float(ticker['buy']),
                'bid_1_amount': None,
                'fluctuation': float(ticker['changeRate']),
                'url': self.urlbase + '/api/v1/market/candles',
            }
            return ticker
        except Exception as e:
            print(f'Kucoin public get ticker error: {e}')


    def get_orderbook(self, symbol: str):
        pass
        # try:
            # orderbook = self.market.get_

    def get_trades(self, symbol: str):
        try:
            trades = self.market.get_trade_histories(self._symbol_convert(symbol))
            print(trades)
        except Exception as e:
            print(f'Kucoin public get trades error: {e}')


    def get_kline(self, symbol: str, time_period=3000, interval=1):
        try:
            klines = self.market.get_kline(symbol, f'{interval}min')
            print(klines)
        except Exception as e:
            print(f'Kucoin public get kline error: {e}')


if __name__ == '__main__':
    ku = KucoinPublic('https://api.kucoin.com')
    # print(ku.get_symbol_info('BTC_USDT'))
    print(ku.get_price('BTC_USDT'))
    # print(ku.get_ticker('BTC_USDT'))
    print(ku.get_orderbook('BTC_USDT'))
    print(ku.get_trades('BTC_USDT'))
    print(ku.get_kline('BTC_USDT'))
import requests
import math
import os
import json


cur_path = os.path.abspath(os.path.dirname(__file__))


class KucoinPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_symbols_info(self):
        try:
            url = self.urlbase + '/spot/v1/symbols/details'
            resp = requests.get(url).json()
            if resp['code'] == 1000:
                data = {}
                for ticker in resp['data']['symbols']:
                    data.update({
                        ticker['symbol']: {
                            'min_amount': float(ticker['base_min_size']),  # 最小下单数量
                            'min_notional': float(ticker['min_buy_amount']),  # 最小下单金额
                            'amount_increment': float(ticker['quote_increment']),  # 数量最小变化
                            'price_increment': round(math.pow(0.1, float(ticker['price_max_precision'])),
                                                     int(ticker['price_max_precision'])),  # 价格最小变化
                            'amount_digit': int(abs(math.log10(float(ticker['base_min_size'])))),  # 数量小数位
                            'price_digit': int(ticker['price_max_precision'])  # 价格小数位
                        }
                    })
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Kucoin batch load symbols error')
        except Exception as e:
            print(f'Kucoin batch load symbols exception {e}')

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
            print(f'Kucoin get symbol info error: {e}')

    def get_price(self, symbol: str):
        pass

    def get_ticker(self, symbol: str):
        pass

    def get_orderbook(self, symbol: str):
        pass

    def get_trades(self, symbol: str):
        pass

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        pass


if __name__ == '__main__':
    ku = KucoinPublic('https://api-cloud.bitmart.info')
    # print(ku.get_symbol_info('MATH_USDT'))
    # print(ku.get_price('BTC_USDT'))
    # print(ku.get_ticker('BTC_USDT'))
    print(ku.get_orderbook('BTC_USDT'))
    # print(ku.get_trades('BTC_USDT'))
    # print(ku.get_kline('BTC_USDT'))
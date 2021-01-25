import requests
import json
import math
import os

cur_path = os.path.abspath(os.path.dirname(__file__))


class LatokenPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_currency(self):
        try:
            url = self.urlbase + '/currency'

            currencies = requests.get(url).json()
            with open(f'{cur_path}\currency_id.json', 'w+') as f:
                json.dump(currencies, f, indent=1)
            f.close()
        except Exception as e:
            print(e)

    def _load_symbols_info(self):
        try:
            self._load_currency()
            with open(f'{cur_path}\currency_id.json', 'r') as f:
                currencies = json.load(f)
            f.close()

            url = self.urlbase + '/pair'
            resp = requests.get(url)
            # if resp.status_code == 200:
            #     data = {}
            #     for ticker in resp.json():
            #         baseCurrency = currencies(ticker['baseCurrency'])
            #         quoteCurrency = currencies(ticker['quoteCurrency'])
            #         data.update({
            #             f'{baseCurrency}_{quoteCurrency}': {
            #                 'min_amount': float(ticker['quantityTick']),  # 最小下单数量
            #                 'min_notional': float(ticker['priceTick']),  # 最小下单金额
            #                 'amount_increment': float(ticker['quantityTick']),  # 数量最小变化
            #                 'price_increment': float(ticker['priceTick']),  # 价格最小变化
            #                 'amount_digit': int(ticker['quantityDecimals']),  # 数量小数位
            #                 'price_digit': int(ticker['priceDecimals'])  # 价格小数位
            #             }
            #         })
            #     with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
            #         json.dump(data, f, indent=1)
            #     f.close()
            # else:
            #     print('Latoken batch load symbols error')
        except Exception as e:
            print(f'Latoken batch load symbols exception {e}')

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
            print(f'Latoken get symbol info error: {e}')

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
    bit = LatokenPublic('https://api.latoken.com/v2')
    bit._load_symbols_info()
    print(bit.get_symbol_info('MATH_USDT'))
    # print(bit.get_price('BTC_USDT'))
    # print(bit.get_ticker('BTC_USDT'))
    print(bit.get_orderbook('BTC_USDT'))
    # print(bit.get_trades('BTC_USDT'))
    # print(bit.get_kline('BTC_USDT'))
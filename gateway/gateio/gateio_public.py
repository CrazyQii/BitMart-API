import requests
import math
import json
import os

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
                with open(f'{cur_path}\symbols_detail.json', 'w+') as f:
                    json.dump(data, f, indent=1)
                f.close()
            else:
                print('Gateio batch load symbols error')
        except Exception as e:
            print(f'Gateio batch load symbols exception {e}')

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


if __name__ == '__main__':
    gate = GateioPublic('https://api.gateio.ws/api/v4')
    gate._load_symbols_info()
    print(gate.get_symbol_info('BTC_USDT'))
    # print(gate.get_price('BTC_USDT'))
    # print(gate.get_ticker('BTC_USDT'))
    # print(gate.get_orderbook('BTC_USDT'))
    # print(gate.get_trades('BTC_USDT'))
    # print(gate.get_kline('BTC_USDT'))
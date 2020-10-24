import requests
import hmac
import hashlib
import time
import json
import os
import math

cur_path = os.path.abspath(os.path.dirname(__file__))


class WootradeAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _symbol_convert(self, symbol: str):
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

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            price_precision = self.get_symbol_info(symbol)['price_digit']  # ".8f"
            symbol = self._symbol_convert(symbol)
            ts = int(time.time()*1000)
            price = round(price, price_precision)
            order = dict()
            order['symbol'] = symbol
            order['order_quantity'] = amount
            order['order_price'] = price
            order['side'] = side.upper()
            order['order_type'] = 'LIMIT'

            msg = ''
            for key in sorted(order.keys()):
                msg += ('&' + key + '=' + str(order[key]))
            msg = msg[1:]
            url = self.urlbase + ('v1/order' + '?' + msg)
            msg += ('|' + str(ts))
            sign = self._sign_message(msg)
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'x-api-key': self.api_key,
                        'x-api-signature': sign,
                        'x-api-timestamp': str(ts),
                        'cache-control': 'no-cache'}
            resp = requests.post(url, data=order, headers=headers).json()
            if resp['success'] is True:
                return resp['order_id']
            else:
                print(f'Wootrade auth error: {resp["message"]}')
                return None
        except Exception as e:
            print(f'Wootrade auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            symbol = self._symbol_convert(symbol)
            ts = int(time.time())

            order = dict()
            order['symbol'] = symbol
            order['order_id'] = order_id

            msg = ''
            for key in sorted(order.keys()):
                msg += ('&' + key + '=' + str(order[key]))
            msg = msg[1:]
            url = self.urlbase + ('v1/order' + '?' + msg)
            msg += ('|' + str(ts))
            sign = self._sign_message(msg)
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'x-api-key': self.api_key,
                        'x-api-signature': sign,
                        'x-api-timestamp': str(ts),
                        'cache-control': 'no-cache'}
            resp = requests.delete(url, data=order, headers=headers).json()
            data = False
            if resp['success'] is True:
                data = resp['success']
                message = resp['message']
            else:
                message = resp['message']
                print(f'Wootrade auth error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Bitmart auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_order',
                    'message': 'Wootrade auth cancel order is empty',
                    'data': False
                }

            for order in orders:
                if str(order['side']).lower() == side:
                    self.cancel_order(symbol, order['order_id'])
            info = {
                'func_name': 'cancel_order',
                'message': 'OK',
                'data': True
            }
            return info
        except Exception as e:
            print(f'Wootrade auth cancel order error: {e}')

    def open_orders(self, symbol: str, status='INCOMPLETE'):
        try:
            symbol = self._symbol_convert(symbol)
            ts = int(time.time())
            order = dict()
            order['symbol'] = symbol
            order['status'] = status

            msg = ''
            for key in sorted(order.keys()):
                msg += ('&' + key + '=' +str(order[key]))
            msg = msg[1:]
            url = self.urlbase + ('v1/orders' + '?' + msg)
            msg += ('|' + str(ts))
            sign = self._sign_message(msg)
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'x-api-key': self.api_key,
                        'x-api-signature': sign,
                        'x-api-timestamp': str(ts),
                        'cache-control': 'no-cache'}
            resp = requests.get(url, headers=headers).json()

            results = []
            if resp['success'] is True:
                for order in resp['rows']:
                    results.append({
                        'order_id': order['order_id'],
                        'symbol': order['symbol'],
                        'amount': float(order['quantity']),
                        'price': float(order['price']),
                        'side': order['side'].lower(),
                        'price_avg': None,
                        'filled_amount': float(order['executed']),
                        'create_time': int(float(order['created_time']))
                    })
            else:
                print(f'Wootrade auth error: {resp["message"]}')
            return results
        except Exception as e:
            print(f'Wootrade auth open order error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            symbol = self._symbol_convert(symbol)
            ts = int(time.time())

            order = dict()
            order['oid'] = id

            msg = ''
            for key in sorted(order.keys()):
                msg += ('&' + key + '=' + str(order[key]))
            msg = msg[1:]
            url = self.urlbase + ('v1/order' + '?' + msg)
            msg += ('|' + str(ts))
            sign = self._sign_message(msg)
            header = {'Content-Type': 'application/x-www-form-urlencoded',
                        'x-api-key': self.api_key,
                        'x-api-signature': sign,
                        'x-api-timestamp': str(ts),
                        'cache-control': 'no-cache'}
            resp = requests.get(url, headers=header).json()
            order_detail = {}
            if resp['success'] is True:
                order_detail = {
                    'order_id': resp['order_id'],
                    'symbol': resp['symbol'],
                    'amount': float(resp['quantity']),
                    'price': float(resp['price']),
                    'side': resp['side'].lower(),
                    'price_avg': None,
                    'filled_amount': float(resp['executed']),
                    'create_time': int(float(resp['created_time']))
                }
            else:
                print(f'Wootrade auth error: {resp["message"]}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp['message'],
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Wootrade auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + "v2/client/holding?all=true"
            ts = int(time.time())
            msg = "all=true|" + str(ts)
            sign = self._sign_message(msg)
            header = {"Content-Type": "application/x-www-form-urlencoded",
                        "x-api-key": self.api_key,
                        "x-api-signature": sign,
                        "x-api-timestamp": str(ts),
                        "cache-control": "no-cache"}
            resp = requests.get(url, headers=header).json()
            balance, frozen = {}, {}
            if resp['success'] is True:
                balance = {row["token"]: float(row["holding"]) for row in resp["holding"]}
                frozen = {row["token"]: float(row["frozen"]) for row in resp["holding"]}
            else:
                print(f'Wootrade auth error: {resp["message"]}')
            return balance, frozen
        except Exception as e:
            print(f'Wootrade auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    woo = WootradeAuth('https://nexus.kronostoken.com', 'AbmyVJGUpN064ks5ELjLfA==', 'QHKRXHPAW1MC9YGZMAT8YDJG2HPR')
    print(woo.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(woo.order_detail('BTC_USDT', '1'))
    # print(woo.open_orders('BTC_USDT'))
    # print(woo.cancel_order('UMA_USDT', '1'))
    # print(woo.cancel_all('BTC_USDT', 'buy'))
    # print(woo.wallet_balance())
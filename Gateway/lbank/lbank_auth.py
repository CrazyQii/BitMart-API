import requests
import hashlib
import hmac
import time
import string
import random
import operator
from urllib.parse import urlencode


class LbankAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_message(self, params: dict, headers: dict):
        params['echostr'] = headers['echostr']
        params['timestamp'] = headers['timestamp']
        params['signature_method'] = headers['signature_method']
        params = sorted(params.items(), key=operator.itemgetter(0))
        params = urlencode(params)
        msg = hashlib.md5(params.encode("utf8")).hexdigest().upper()
        signature = hmac.new(bytes(self.api_secret, encoding='utf8'),
                             bytes(msg, encoding='utf8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def _request(self, method: str, url: str, params: dict = None):
        if params is None:
            params = dict()
        try:
            t = str(time.time() * 1000).split('.')[0]
            num = string.ascii_letters + string.digits
            echostr = ''.join(random.sample(num, 35))

            headers = {
                'Content-type': 'application/x-www-form-urlencoded',
                'signature_method': 'HmacSHA256',
                'timestamp': t,
                'echostr': echostr
            }
            params['api_key'] = self.api_key
            params['sign'] = self._sign_message(params, headers)

            if method == 'POST':
                resp = requests.post(url, data=params, headers=headers).json()
            else:
                resp = requests.get(url, params=params, headers=headers).json()
            return resp
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/create_order.do'
            params = {
                'symbol': symbol.lower(),
                'type': side.lower(),
                'price': price,
                'amount': amount
            }
            resp = self._request('POST', url, params)
            print(resp)
            if resp['result'] and 'data' in resp:
                return resp['data']['order_id']
            else:
                print(f'Lbank auth place order error: {resp}')
            return None
        except Exception as e:
            print(f'Lbank auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/cancel_order.do'
            params = {
                'symbol': symbol.lower(),
                'order_id': order_id
            }

            resp = self._request('POST', url, params)
            data = False
            if resp['result'] and 'data' in resp:
                data = True
                message = resp['data']
            else:
                message = resp
                print(f'Lbank auth cancel order error: {resp}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Lbank auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_all',
                    'message': 'Empty order',
                    'data': False
                }
            data = True
            for order in orders:
                if str(order['side']).lower() == side:
                    result = self.cancel_order(symbol, order['order_id'])['data']
                    if result is False:
                        data = False
            info = {
                'func_name': 'cancel_all',
                'message': 'OK',
                'data': data
            }
            return info
        except Exception as e:
            print(f'Lbank auth cancel all error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, [1, 3], page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print(f'Lbank auth open orders error: {e}')

    def order_list(self, symbol: str, status=None, offset=1, limit=100):
        if status is None:
            status = [0, 1]
        try:
            url = self.urlbase + '/orders_info_no_deal.do'
            params = {
                'symbol': symbol.lower(),
                'current_page': offset,
                'page_length': limit
            }
            resp = self._request('POST', url, params)
            results = []
            if resp['result'] and 'data' in resp:
                for order in resp['data']:
                    if order['status'] in status:
                        results.append({
                            'order_id': order['order_id'],
                            'symbol': symbol,
                            'side': order['type'],
                            'price': float(order['price']),
                            'amount': float(order['amount']),
                            'price_avg': float(order['avg_price']),
                            'filled_amount': float(order['deal_amount']),
                            'timestamp': round(order['create_time'] / 1000)
                        })
            else:
                print(f'Lbank auth open orders error: {resp}')
            return results
        except Exception as e:
            print(f'Lbank auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/orders_info.do'
            params = {
                'symbol': symbol.lower(),
                'order_id': order_id
            }

            resp = self._request('POST', url, params)
            order_detail = []
            if resp['result'] and 'data' in resp:
                order = resp['data']
                order_detail = {
                    'order_id': order['order_id'],
                    'symbol': symbol,
                    'side': order['type'],
                    'price': float(order['price']),
                    'amount': float(order['amount']),
                    'price_avg': float(order['avg_price']),
                    'filled_amount': float(order['deal_amount']),
                    'status': order['status'],
                    'timestamp': round(order['create_time'] / 1000)
                }
            else:
                print(f'Lbank auth order detail error: {resp}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Lbank auth order detail error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/transaction_history.do'
            params = {
                'symbol': symbol.lower(),
                'type': 'buy',
                'size': limit
            }
            resp = self._request('POST', url, params)
            trades = []
            # 买方成交记录
            if resp['result'] and 'data' in resp:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': trade['txUuid'],
                        'order_id': trade['orderUuid'],
                        'symbol': symbol,
                        'create_time': round(trade['dealTime'] / 1000),
                        'side': trade['tradeType'],
                        'price_avg': None,
                        'notional': float(trade['dealPrice']),
                        'amount': float(trade['dealQuantity']),
                        'fees': float(trade['tradeFee']),
                        'fee_coin_name': None,
                        'exec_type': None
                    })
            else:
                print(f'Lbank auth user trades error: {resp}')
            # 卖方成交记录
            params['type'] = 'sell'
            resp = self._request('POST', url, params)
            if resp['result'] and 'data' in resp:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': trade['txUuid'],
                        'order_id': trade['orderUuid'],
                        'symbol': symbol,
                        'create_time': round(trade['dealTime'] / 1000),
                        'side': trade['tradeType'],
                        'price_avg': None,
                        'notional': float(trade['dealPrice']),
                        'amount': float(trade['dealQuantity']),
                        'fees': float(trade['tradeFee']),
                        'fee_coin_name': None,
                        'exec_type': None
                    })
            else:
                print(f'Lbank auth user trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Lbank auth user trades error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/user_info.do'
            resp = self._request('POST', url)
            balance, frozen = {}, {}
            if resp['result'] and 'data' in resp:
                wallet = resp['data']
                balance = {key: float(value) for key, value in wallet['free'].items()}
                frozen = {key: float(value) for key, value in wallet['freeze'].items()}
            else:
                print(f'Okex auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Okex auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    # 授权失败，非签名失败
    # {'result': 'false', 'error_code': 10022, 'ts': 1606965076008}
    bit = LbankAuth('https://www.lbkex.net/v2', 'd031d523-9291-409c-8238-1642fd4c31e0',
                      'D09079DFDE436D5B4BDEAC6EA75CA5AF')
    # print(bit.place_order('BTC_USDT', 1.0016, 11, 'sell'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('BTC_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.user_trades('BTC_USDT'))
    # print(bit.wallet_balance())
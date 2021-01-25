import hmac
import hashlib
import json
import requests
from urllib.parse import urlencode
from datetime import datetime


class CoinbeneAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _symbol_convert(self, symbol: str):
        return '/'.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _sign_message(self, message):
        try:
            # signature method
            digest = hmac.new(bytes(self.api_secret, encoding='utf-8'), bytes(message, encoding='utf-8'),
                              digestmod=hashlib.sha256).hexdigest()
            return digest
        except Exception as e:
            print(e)

    def _request(self, method: str, path: str, params: dict = None):
        try:
            url = self.urlbase + path
            timestamp = datetime.utcnow().isoformat('T', 'milliseconds') + 'Z'
            if method == 'POST':
                msg = timestamp + method + path + ('' if params is None else json.dumps(params))
                headers = {
                    'ACCESS-KEY': self.api_key,
                    'ACCESS-SIGN': self._sign_message(msg),
                    'ACCESS-TIMESTAMP': timestamp,
                    'Content-type': 'application/json'
                }
                resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            else:
                msg = timestamp + method + path + ('' if params is None else '?' + urlencode(params))
                headers = {
                    'ACCESS-KEY': self.api_key,
                    'ACCESS-SIGN': self._sign_message(msg),
                    'ACCESS-TIMESTAMP': timestamp,
                    'Content-type': 'application/json'
                }
                resp = requests.get(url, params=params, headers=headers).json()
            return resp
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        if side not in ['buy', 'sell']:
            print('side is wrong')
            return None
        try:
            params = {
                'symbol': self._symbol_convert(symbol),
                'direction': 1 if side == 'buy' else 2,
                'orderType': 1,
                'price': price,
                'quantity': amount
            }
            resp = self._request('POST', '/api/exchange/v2/order/place', params)
            if resp['code'] == 200:
                return resp['data']['orderId']
            else:
                print(f'Coinbene auth place order error: {resp}')
            return None
        except Exception as e:
            print(f'Coinbene auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            params = {
                'orderId': order_id
            }
            resp = self._request('POST', '/api/exchange/v2/order/cancel', params)
            data = False
            if resp['code'] == 200:
                data = True
                message = resp
            else:
                message = resp
                print(f'Coinbene auth error: {message}')

            info = {
                'func_name': 'cancel_order',
                'order_id': order_id,
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Coinbene auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                info = {
                    'func_name': 'cancel_all',
                    'message': 'Empty order',
                    'data': False
                }
                return info

            orderIds = []
            for order in orders:
                if order['side'] == side:
                    orderIds.append(order['order_id'])

            params = {'orderIds': orderIds}
            resp = self._request('POST', '/api/exchange/v2/order/batchCancel', params)
            data = False
            if resp['code'] == 200:
                data = True
                message = 'ok'
            else:
                message = resp
                print(f'Coinbene auth cancel all error: {message}')

            info = {
                'func_name': 'cancel_all',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Coinbene auth cancel all error: {e}')

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                if len(orders) == 0:
                    orders_on_this_page = self.order_list(symbol)
                else:
                    last_id = orders[-1]['order_id']
                    orders_on_this_page = self.order_list(symbol, latestOrderId=last_id)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
                else:
                    break
            return orders
        except Exception as e:
            print(f'Okex auth open orders error: {e}')

    def order_list(self, symbol: str, status=None, latestOrderId=None):
        if status is None:
            status = ['Cancelled', 'Partially cancelled']
        try:
            params = {
                'symbol': self._symbol_convert(symbol)
            }
            #  订单分页查询
            '' if latestOrderId is None else params.update({'latestOrderId': latestOrderId})
            resp = self._request('GET', '/api/exchange/v2/order/openOrders', params)
            results = []
            if resp['code'] == 200:
                for order in resp['data']:
                    if order['orderStatus'] in status:
                        results.append({
                            'order_id': order['orderId'],
                            'symbol': f'{order["baseAsset"]}_{order["quoteAsset"]}',
                            'amount': float(order['amount']),
                            'price': float(order['price']),
                            'side': order['orderDirection'],
                            'price_avg': float(order['avgPrice']),
                            'filled_amount': float(order['filledAmount']),
                            'create_time': self._utc_to_ts(order['orderTime'])
                        })
            else:
                print(f'Coinbene auth open order error: {resp}')
            return results
        except Exception as e:
            print(f'Coinbene auth open order error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        # 按用户请求进行订单成交明细列表查询
        order_ids = self.open_orders(symbol)
        trades = []
        try:
            for order_id in order_ids:
                params = {'orderId': order_id}
                resp = self._request('GET', '/api/exchange/v2/order/trade/fills', params)
                if resp['code'] == 200:
                    for trade in resp['data']:
                        trades.append({
                            'detail_id': None,
                            'order_id': order_id,
                            'symbol': symbol,
                            'create_time': self._utc_to_ts(trade['tradeTime']),
                            'side': trade['direction'],
                            'price_avg': None,
                            'notional': float(trade['price']),
                            'size': float(trade['quantity']),
                            'fees': float(trade['fee']),
                            'fee_coin_name': trade['feeByConi'],
                            'exec_type': None
                        })
                else:
                    print(f'Coinbene auth user trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Coinbene auth user trades error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            params = {
                'orderId': order_id
            }
            resp = self._request('GET', '/api/exchange/v2/order/info', params)
            order_detail = {}
            if resp['code'] == 200:
                content = resp['data']
                order_detail = {
                    'order_id': content['orderId'],
                    'symbol': f'{content["baseAsset"]}_{content["quoteAsset"]}',
                    'amount': float(content['amount']),
                    'price': float(content['price']),
                    'side': content['orderDirection'],
                    'price_avg': float(content['avgPrice']),
                    'filled_amount': float(content['filledAmount']),
                    'status': resp['orderStatus'],
                    'create_time': self._utc_to_ts(content['orderTime'])
                }
                message = 'ok'
            else:
                message = resp
                print(f'Coinbene auth order detail error: {message}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': message,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Coinbene auth order detail error: {e}')

    def wallet_balance(self):
        try:
            resp = self._request('GET', '/api/exchange/v2/account/list')
            balance, frozen = {}, {}
            if resp['code'] == 200:
                wallet = resp['data']
                balance = {row['asset']: float(row['available']) for row in wallet}
                frozen = {row['asset']: float(row['frozenBalance']) for row in wallet}
            else:
                print(f'Coinbene auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Coinbene auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    # 网络错误，没有办法测试
    bit = CoinbeneAuth('https://openapi-exchange.coinbene.com', '8ce194f269f2a06387575fb5230a81b6', '71690075331647309e11b23238dcdced', 'mock')
    # print(bit.place_order('BTC_USDT', 1.03, 11, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.user_trades('BTC_USDT'))
    # print(bit.wallet_balance())

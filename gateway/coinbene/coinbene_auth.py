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
        self.memo = passphrase

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

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        if side not in ['buy', 'sell']:
            print('side is wrong')
            return None
        try:
            url = self.urlbase + '/api/exchange/v2/order/place'
            params = {
                'symbol': self._symbol_convert(symbol),
                'direction': 1 if side == 'buy' else 2,
                'orderType': 1,
                'price': price,
                'quantity': amount
            }
            timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            msg = timestamp + 'POST' + '/api/exchange/v2/order/place' + json.dumps(params)
            headers = {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': self._sign_message(msg),
                'ACCESS-TIMESTAMP': timestamp,
                'Content-type': 'application/json'
            }
            resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            if resp['code'] == 200:
                return resp['data']['orderId']
            else:
                print(f'Coinbene auth place order error: {resp}')
                return None
        except Exception as e:
            print(f'Coinbene auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/api/exchange/v2/order/cancel'
            params = {
                'orderId': order_id
            }
            timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            msg = timestamp + 'POST' + '/api/exchange/v2/order/cancel' + json.dumps(params)
            headers = {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': self._sign_message(msg),
                'ACCESS-TIMESTAMP': timestamp,
                'Content-type': 'application/json'
            }
            resp = requests.post(url, data=json.dumps(params), headers=headers).json()
            data = False
            if resp['code'] == 200:
                data = resp['data']
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
            url = self.urlbase + '/api/exchange/v2/order/batchCancel'
            orders = self.open_orders(symbol)
            orderIds = []
            for order in orders:
                if order['side'] == side:
                    orderIds.append(order['order_id'])

            params = {
                'orderIds': orderIds
            }
            timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            msg = timestamp + 'POST' + '/api/exchange/v2/order/batchCancel' + json.dumps(params)
            headers = {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': self._sign_message(msg),
                'ACCESS-TIMESTAMP': timestamp,
                'Content-type': 'application/json'
            }
            resp = requests.post(url, data=json.dumps(params), headers=headers).json()

            data = False
            if resp['code'] == 200:
                data = resp['data']
                message = resp
            else:
                message = resp['message']
                print(f'Coinbene auth error: {message}')

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Coinbene auth cancel order error: {e}')

    def open_orders(self, symbol: str, status='Open', offset=1, limit=100):
        try:
            url = self.urlbase + '/api/exchange/v2/order/closedOrders'
            params = {
                'symbol': self._symbol_convert(symbol)
            }
            timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            msg = timestamp + 'GET' + '/api/exchange/v2/order/closedOrder?' + urlencode(params)
            headers = {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': self._sign_message(msg),
                'ACCESS-TIMESTAMP': timestamp,
                'Content-type': 'application/json'
            }
            resp = requests.get(url, params=params, headers=headers).json()
            results = []
            if resp['code'] == 200:
                i = 0
                for order in resp['data']:
                    if i >= limit:
                        break
                    if order['orderStatus'] == status:
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
                        i = i + 1
            else:
                print(f'Coinbene auth open order error: {resp}')
            return results
        except Exception as e:
            print(f'Coinbene auth open order error: {e}')

    def user_trades(self, symbol: str, offset=1, limit=100):
        try:
            url = self.urlbase + '/spot/v1/trades'
            params = {'symbol': symbol, 'limit': limit, 'offset': offset}
            headers = {
                'X-BM-KEY': self.api_key,
                'X-BM-TIMESTAMP': self._timestamp(),
                'Content-type': 'application/json'
            }

            resp = requests.get(url, params=params, headers=headers).json()
            trades = []
            if resp['code'] == 200:
                for trade in resp['data']:
                    trades.append({
                        'detail_id': trade['detail_id'],
                        'order_id': trade['order_id'],
                        'symbol': symbol,
                        'create_time': int(trade['create_time'] / 1000),
                        'side': trade['side'],
                        'price_avg': float(trade['price_avg']),
                        'notional': float(trade['notional']),
                        'size': float(trade['size']),
                        'fees': float(trade['fees']),
                        'fee_coin_name': trade['fee_coin_name'],
                        'exec_type': trade['exec_type']
                    })
            else:
                print(f'Coinbene auth user trades error: {resp}')
            return trades
        except Exception as e:
            print(f'Coinbene auth user trades error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/api/exchange/v2/order/info'
            params = {
                'orderId': order_id
            }
            timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            msg = timestamp + 'GET' + '/api/exchange/v2/order/info?' + urlencode(params)
            headers = {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': self._sign_message(msg),
                'ACCESS-TIMESTAMP': timestamp,
                'Content-type': 'application/json'
            }

            resp = requests.get(url, params=params, headers=headers).json()
            order_detail = {}
            if resp['code'] == 200:
                content = resp['data']
                if content['orderId'] is not None:
                    order_detail = {
                        'order_id': content['orderId'],
                        'symbol': f'{content["baseAsset"]}_{content["quoteAsset"]}',
                        'amount': float(content['amount']),
                        'price': float(content['price']),
                        'side': content['orderDirection'],
                        'price_avg': float(content['avgPrice']),
                        'filled_amount': float(content['filledAmount']),
                        'create_time': self._utc_to_ts(content['orderTime'])
                    }
            else:
                print(f'Coinbene auth order detail error: {resp}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Coinbene auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/api/exchange/v2/account/list'
            timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            msg = timestamp + 'GET' + '/api/exchange/v2/account/list'
            headers = {
                'ACCESS-KEY': self.api_key,
                'ACCESS-SIGN': self._sign_message(msg),
                'ACCESS-TIMESTAMP': timestamp,
                'Content-type': 'application/json'
            }
            resp = requests.get(url, headers=headers).json()
            balance, frozen = {}, {}
            if resp['code'] == 200:
                wallet = resp["data"]
                balance = {row["asset"]: float(row["available"]) for row in wallet}
                frozen = {row["asset"]: float(row["frozenBalance"]) for row in wallet}
            else:
                print(f'Coinbene auth wallet balance error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Coinbene auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = CoinbeneAuth('https://openapi-exchange.coinbene.com', '8ce194f269f2a06387575fb5230a81b6', '71690075331647309e11b23238dcdced', 'mock')
    # print(bit.place_order('BTC_USDT', 1.03, 11, 'buy'))
    # print(bit.order_detail('BTC_USDT', '1'))
    print(bit.open_orders('BTC_USDT'))  # 未处理解决
    # print(bit.cancel_order('UMA_USDT', '1'))
    print(bit.cancel_all('BTC_USDT', 'buy'))
    print(bit.user_trades('BTC_USDT'))
    # print(bit.wallet_balance())

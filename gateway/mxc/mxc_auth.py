import requests
import hmac
import hashlib
import time
import json


class MxcAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, method, path, params):
        if method == 'POST':
            msg = f'{method}\n{path}\napi_key={params["api_key"]}&req_time={params["req_time"]}'
        else:
            paramStr = ''
            paramStr += '&'.join([f'{key}={value}' for key, value in params.items()])
            msg = f'{method}\n{path}\n&{paramStr}'
        print(msg)
        sign = hmac.new(bytes(self.api_secret, encoding='utf-8'),
                        bytes(msg, encoding='utf-8'), hashlib.sha256).hexdigest()
        return sign

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/open/api/v2/order/place'
            params = {
                'api_key': self.api_key,
                'req_time': str(int(time.time())),
                'symbol': symbol,
                'price': price,
                'quantity': amount,
                'trade_type': 'BID' if side == 'buy' else 'ASK',
                'order_type': 'LIMIT_ORDER'
            }

            sign = self._sign_message('POST', '/open/api/v2/order/place', params)
            params.update({'sign': sign})
            print(params)

            resp = requests.post(url, data=json.dumps(params)).json()
            print(resp)
            if resp['code'] == 200:
                print(resp)
            else:
                print(f'Mxc auth error: {resp["msg"]}')
                return None
        except Exception as e:
            print(f'Mxc auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/open/api/v2/order/cancel'
            params = {
                'api_key': self.api_key,
                'req_time': str(int(time.time())),
                'order_ids': order_id
            }

            sign = self._sign_message('DELETE', '/open/api/v2/order/cancel', params)
            params.update({'sign': sign})

            print(params)
            resp = requests.delete(url, params=params).json()
            data = False
            if resp['code'] == 200:
                data = resp['data']
                message = resp['msg']
            else:
                message = resp['msg']
                print(f'Mxc auth error: {resp["msg"]}')

            info = {
                'func_name': 'cancel_order',
                'message': message,
                'data': data
            }
            return info
        except Exception as e:
            print(f'Mxc auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        pass

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        pass

    def order_detail(self, symbol: str, order_id: str):
        pass

    def wallet_balance(self):
        pass


if __name__ == '__main__':
    mxc = MxcAuth('https://www.mxcio.co', 'mx0Iw5GHIlySTepTAN', 'ec4f09f088d642d2b2ebfae695b9c511')
    print(mxc.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(mxc.order_detail('BTC_USDT', '1'))
    # print(mxc.open_orders('BTC_USDT'))
    print(mxc.cancel_order('UMA_USDT', '1'))
    # print(mxc.cancel_all('BTC_USDT', 'buy'))
    # print(mxc.wallet_balance())
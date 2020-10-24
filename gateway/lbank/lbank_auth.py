import requests
import hashlib
import hmac
import time
import string
import random

class LbankAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, params, timestamp, echostr):
        p = params
        p['echostr'] = echostr
        p["timestamp"] = timestamp
        p["signature_method"] = 'HmacSHA256'
        par = []
        for k in sorted(p.keys()):
            par.append(k + '=' + str(p[k]))
        par = '&'.join(par)
        msg = hashlib.md5(par.encode("utf8")).hexdigest().upper()

        appsecret = bytes(self.api_secret, encoding='utf8')
        data = bytes(msg, encoding='utf8')
        signature = hmac.new(appsecret, data, digestmod=hashlib.sha256).hexdigest().lower()

        return signature

    def _get_header(self):
        t = str(time.time() * 1000).split(".")[0]

        num = string.ascii_letters + string.digits
        randomstr = "".join(random.sample(num, 35))

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            "signature_method": "HmacSHA256",
            'timestamp': t,
            'echostr': randomstr
        }
        return headers

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            headers = self._get_header()
            par = dict()
            par["api_key"] = self.api_key
            par["symbol"] = symbol.lower()
            par["type"] = side.lower()
            par["price"] = price
            par["amount"] = amount

            sign = self._sign_message(par, headers['timestamp'], headers['echostr'])
            par["sign"] = sign

            url = self.urlbase + "/create_order.do"

            resp = requests.post(url, data=par, headers=headers).json()
            if resp["result"] is True:
                return resp["data"]["order_id"]
            else:
                print(f'Lbank auth error: {resp}')
            return None
        except Exception as e:
            print(f'Lbank auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + '/cancel_order.do'
            headers = self._get_header()
            par = dict()
            par["api_key"] = self.api_key
            par["symbol"] = symbol.lower()
            par["order_id"] = order_id

            sign = self._sign_message(par, headers['timestamp'], headers['echostr'])
            par["sign"] = sign

            resp = requests.post(url, data=par, headers=headers).json()
            data = False
            if resp["result"] is True:
                data = resp['result']
                message = resp['data']
            else:
                message = resp
                print(f'Lbank auth error: {resp}')

            info = {
                "func_name": "cancel_order",
                "order_id": order_id,
                "message": message,
                "data": data
            }
            return info
        except Exception as e:
            print(f'Lbank auth cancel order error: {e}')

    def cancel_all(self, symbol: str, side: str):
        try:
            orders = self.open_orders(symbol)
            if len(orders) == 0:
                return {
                    'func_name': 'cancel_order',
                    'message': 'Lbank auth cancel order is empty',
                    'data': False
                }
            for order in orders:
                if str(order['type']).lower() == side:
                    self.cancel_order(symbol, order['order_id'])
            info = {
                'func_name': 'cancel_order',
                'message': 'OK',
                'data': True
            }
            return info
        except Exception as e:
            print(f'Lbank auth cancel order error: {e}')

    def open_orders(self, symbol: str, status=0, offset=1, limit=100):
        try:
            url = self.urlbase + "/orders_info_no_deal.do"
            headers = self._get_header()
            par = dict()
            par["api_key"] = self.api_key
            par["symbol"] = symbol.lower()
            par['current_page'] = offset
            par['page_length'] = limit

            sign = self._sign_message(par, headers['timestamp'], headers['echostr'])
            par["sign"] = sign

            resp = requests.post(url, data=par, headers=headers).json()
            results = []
            if resp["result"] is True:
                for order in resp['data']:
                    results.append({
                        "order_id": order['order_id'],
                        "symbol": symbol,
                        "side": order["type"],
                        "price": float(order["price"]),
                        "amount": float(order["amount"]),
                        "price_avg": float(order["avg_price"]),
                        "filled_amount": float(order["deal_amount"]),
                        "timestamp": round(order['create_time'] / 1000)
                    })
            else:
                print(f'Lbank auth error: {resp}')
            return results
        except Exception as e:
            print(f'Lbank auth open orders error: {e}')

    def order_detail(self, symbol: str, order_id: str):
        try:
            url = self.urlbase + "/orders_info.do"
            headers = self._get_header()
            par = dict()
            par["api_key"] = self.api_key
            par["symbol"] = symbol.lower()
            par['order_id'] = order_id

            sign = self._sign_message(par, headers['timestamp'], headers['echostr'])
            par["sign"] = sign

            resp = requests.post(url, data=par, headers=headers).json()
            order_detail = []
            if resp["result"] is True:
                order = resp['data']
                order_detail = {
                    "order_id": order['order_id'],
                    "symbol": symbol,
                    "side": order["type"],
                    "price": float(order["price"]),
                    "amount": float(order["amount"]),
                    "price_avg": float(order["avg_price"]),
                    "filled_amount": float(order["deal_amount"]),
                    "timestamp": round(order['create_time'] / 1000)
                }
            else:
                print(f'Lbank auth error: {resp}')
            info = {
                'func_name': 'order_detail',
                'order_id': order_id,
                'message': resp,
                'data': order_detail
            }
            return info
        except Exception as e:
            print(f'Lbank auth order detail error: {e}')

    def wallet_balance(self):
        try:
            url = self.urlbase + '/user_info.do'
            headers = self._get_header()
            par = dict()
            par["api_key"] = self.api_key

            sign = self._sign_message(par, headers['timestamp'], headers['echostr'])
            par["sign"] = sign

            resp = requests.post(url, data=par, headers=headers).json()
            balance, frozen = {}, {}
            if resp['result'] is True:
                wallet = resp['data']
                balance = {key: float(value) for key, value in wallet['free'].items()}
                frozen = {key: float(value) for key, value in wallet['freeze'].items()}
            else:
                print(f'Okex auth error: {resp}')
            return balance, frozen
        except Exception as e:
            print(f'Okex auth wallet balance error: {e}')
            return {}, {}


if __name__ == '__main__':
    bit = LbankAuth('https://www.lbkex.net/v2', 'd031d523-9291-409c-8238-1642fd4c31e0',
                      'D09079DFDE436D5B4BDEAC6EA75CA5AF')
    # print(bit.place_order('BTC_USDT', 1.0016, 11, 'sell'))
    # print(bit.order_detail('BTC_USDT', '1'))
    # print(bit.open_orders('BTC_USDT'))
    # print(bit.cancel_order('UMA_USDT', '1'))
    # print(bit.cancel_all('BTC_USDT', 'buy'))
    # print(bit.wallet_balance())
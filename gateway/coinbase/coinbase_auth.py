import requests
import hashlib
import hmac
import base64
import json
import time


class CoinbaseAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def _symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))

    def _sign_message(self, timestamp, method, path, data=''):
        try:
            message = timestamp + method.upper() + path + data
            print(message)
            message = message.encode('ascii')
            hmac_key = base64.b64decode(self.api_secret)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")

            headers = {
                'CB-ACCESS-SIGN': signature_b64,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-KEY': self.api_key,
                'CB-ACCESS-PASSPHRASE': self.memo,
                'Content-Type': 'application/json'
            }
            return headers
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        try:
            url = self.urlbase + '/orders'
            params = {
                'product_id': self._symbol_convert(symbol),
                'side': side,
                'type': 'limit',
                'price': price,
                'size': amount
            }
            timestamp = str(int(time.time() ))
            headers = self._sign_message(timestamp, 'POST', '/orders', json.dumps(params))

            resp = requests.post(url, data=json.dumps(params), headers=headers)
            print(resp.json())
            if resp.status_code == 200:
                resp = resp.json()
                return resp['orderId']
            else:
                print(f'Binance auth error: {resp.json()["msg"]}')
                return None
        except Exception as e:
            print(f'Binance auth place order error: {e}')

    def cancel_order(self, symbol: str, order_id: str):
        pass

    def cancel_all(self, symbol: str, side: str):
        pass

    def open_orders(self, symbol: str, status=9, offset=1, limit=100):
        pass

    def order_detail(self, symbol: str, order_id: str):
        pass

    def wallet_balance(self):
        pass


if __name__ == '__main__':
    binance = CoinbaseAuth('https://api-public.sandbox.pro.coinbase.com', 'M9ca21rGt4fGg9mJ',
                          '9FWUPE56IqfncEqglxBJ6DGDJq2NDufR', 'demo')
    print(binance.place_order("BTC_USDT", 30, 0.01, "buy"))
    # print(binance.order_detail('BTC_USDT', '1'))
    # print(binance.open_orders('BTC_USDT'))
    # print(binance.cancel_order('BTC_USDT', '1'))
    # print(binance.cancel_all('BTC_USDT', 'sell'))
    # print(binance.wallet_balance())
"""
HuoBi authentication api
2020/10/13 hlq
"""

from huobi.huo_public import HuoPublic
import datetime
import hmac
import hashlib
import base64
from urllib import parse


class HuoAuth(HuoPublic):
    def __init__(self, urlbase, api_key, api_secret):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret

    def _get_timestamp(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def _set_params(self, signature, params: dict=None):
        """ parse string to correct format"""
        try:
            res = {
                'AccessKeyId': self.api_key,
                "SignatureVersion": "2",
                "SignatureMethod": "HmacSHA256",
                "Timestamp": self._get_timestamp(),
            }
            if params is not None:
                for key, value in params.items():
                    res.update({key: value})
            res.update({'Signature': signature})
            return res
        except Exception as e:
            print(e)

    def _sign_message(self, method, host, path, params=None):
        try:
            if params is None:
                req_str = f'AccessKeyId={self.api_key}&' \
                          f'SignatureMethod=HmacSHA256&' \
                          f'SignatureVersion=2&' \
                          f'Timestamp={parse.quote(self._get_timestamp())}'
            else:
                par_str = '&'.join([f'{key}={value}' for key, value in params.items()])
                req_str = f'AccessKeyId={self.api_key}&' \
                          f'SignatureMethod=HmacSHA256&' \
                          f'SignatureVersion=2&' \
                          f'Timestamp={parse.quote(self._get_timestamp())}&' \
                          f'{par_str}'
            # concat string
            msg = f'{method}\n{host}\n{path}\n{req_str}'
            digest = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'),
                              digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(digest).decode()
            return sign
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str, account_id=16267039):
        try:
            url = self.urlbase + '/v1/order/orders/place'

            params = {
                'account-id': account_id,
                'amount': amount,
                'price': price,
                'source': 'spot-api',
                'symbol': self._symbol_convert(symbol),
                'type': f'{side}-limit'
            }

            signature = self._sign_message('POST', 'api.huobi.pro', '/v1/order/orders/place', params)
            params = self._set_params(signature, params)

            is_ok, content = self._request('POST', url, data=params, headers={'Content-Type': 'application/json'})
            if is_ok and content['status'] == 'ok':
                return content
            else:
                self._output('place_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, symbol: str, entrust_id: str):
        try:
            url = self.urlbase + f'/v1/order/orders/{entrust_id}/submitcancel'

            signature = self._sign_message('POST', 'api.huobi.pro', f'/v1/order/orders/{entrust_id}/submitcancel')
            params = self._set_params(signature)

            is_ok, content = self._request('POST', url, params=params)
            if is_ok and content['status'] == 'ok':
                info = {
                    "func_name": 'cancel_order',
                    "entrust_id": entrust_id,
                    "response": content
                }
                print(info)
                return is_ok
            else:
                self._output('cancel_order', content)
        except Exception as e:
            print(e)

    def open_orders(self, symbol: str, start_time=None, end_time=None, direct=None, size=None):
        try:
            url = self.urlbase + '/v1/order/history'

            params = {
                'symbol': self._symbol_convert(symbol),
            }

            signature = self._sign_message('GET', 'api.huobi.pro', '/v1/order/history', params)
            params = self._set_params(signature, params)

            is_ok, content = self._request('GET', url, params=params, headers={'Content-Type': 'application/json'})
            if is_ok and content['status'] == 'ok':
                results = []
                for order in content['data']:
                    results.append({
                        'entrust_id': order['id'],
                        'side': order['type'],
                        'symbol': order['symbol'],
                        'status': order['state'],
                        'timestamp': order['created-at'],
                        'price': order['price'],
                        'original_amount': order['amount'],
                        'executed_amount': order['field-amount'],
                        'remaining_amount': float(order['amount']) - float(order['field-amount']),
                        'fees': order['field-fees']
                    })
                return results
            else:
                return self._output('open_orders', content)
        except Exception as e:
            print(e)

    def order_detail(self, symbol: str, entrust_id: str):
        try:
            url = self.urlbase + f'/v1/order/orders/{entrust_id}'

            signature = self._sign_message('GET', 'api.huobi.pro', f'/v1/order/orders/{entrust_id}')
            params = self._set_params(signature)

            is_ok, content = self._request('GET', url, params=params, headers={'Content-Type': 'application/json'})
            if is_ok and content['status'] == 'ok':
                print(content)
                order = content['data']
                return {
                    'entrust_id': order['id'],
                    'side': order['type'],
                    'symbol': order['symbol'],
                    'status': order['state'],
                    'timestamp': order['created-at'],
                    'price': order['price'],
                    'original_amount': order['amount'],
                    'executed_amount': order['field-amount'],
                    'remaining_amount': float(order['amount']) - float(order['field-amount']),
                    'fees': order['field-fees']
                }
            else:
                self._output('order_detail', content)
        except Exception as e:
            print(e)

    def wallet_info(self):
        try:
            url = self.urlbase + '/v1/account/accounts'
            signature = self._sign_message('GET', 'api.huobi.pro', '/v1/account/accounts')
            params = self._set_params(signature)
            is_ok, content = self._request('GET', url, params=params, headers={'Content-Type': 'application/json'})
            if is_ok and content['status'] == 'ok':
                return content['data']
            else:
                self._output('wallet_info', content)

        except Exception as e:
            print(e)

    def wallet_balance(self, account_id=16267039):
        try:
            url = self.urlbase + f'/v1/account/accounts/{account_id}/balance'
            signature = self._sign_message('GET', 'api.huobi.pro', f'/v1/account/accounts/{account_id}/balance')
            params = self._set_params(signature)
            is_ok, content = self._request('GET', url, params=params, headers={'Content-Type': 'application/json'})
            if is_ok and content['status'] == 'ok':
                free, frozen = {}, {}
                for currency in content['data']['list']:
                    if currency['type'] == 'trade':
                        free[currency['currency']] = currency['balance']
                    if currency['type'] == 'frozen':
                        frozen[currency['currency']] = currency['balance']
                return free, frozen
            else:
                self._output('wallet_balance', content)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    huo = HuoAuth('https://api.huobi.pro', '', '')
    wallet_id = huo.wallet_info()[0]['id']
    # print(huo.place_order('EOS_USDT', 1.0016, 11, 'sell', account_id=wallet_id))
    # print(huo.cancel_order('EOS_USDT', '234'))
    # print(huo.open_orders('EOS_USDT'))
    # print(huo.order_detail('EOS_USDT', '234'))
    # print(huo.wallet_balance())
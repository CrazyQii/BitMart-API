# -*- coding: utf-8 -*-
"""
授权接口
2020-10-4 hlq
"""

from quoine.quoine_public import QuoinePublic
import jwt
import time
import json


class QuoineAuth(QuoinePublic):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        super().__init__(urlbase)
        self.token_id = api_key
        self.user_secret = api_secret
        self.passphrase = passphrase

    def _sign_message(self, path):
        """ Authentication """
        try:
            payload = {
                'path': path,
                'nonce': round(time.time() * 1000),
                'token_id': self.token_id
            }
            sign = jwt.encode(payload, self.user_secret, algorithm='HS256').decode('ascii')
            return sign
        except Exception as e:
            print(e)

    def _get_all_accounts(self):
        """ get all accounts' currency """
        try:
            url = self.urlbase + '/accounts/balance'
            sign_message = self._sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self._request('GET', url, headers=headers)
            if is_ok:
                currencies = []
                for account in content:
                    currencies.append(account['currency'])
                return currencies
            else:
                return {}
        except Exception as e:
            print(e)

    def place_order(self, symbol: str, amount: float, price: float, side: str, **kwargs):
        try:
            url = self.urlbase + '/orders/'
            sign_message = self._sign_message(url)
            params = {
                'order': {
                    'order_type': 'limit',
                    'product_id': self._product_id(self._symbol_convert(symbol)),
                    'side': side,
                    'quantity': amount,
                    'price': price
                }
            }
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            if kwargs:
                params.update(kwargs)

            is_ok, content = self._request('POST', url, data=json.dumps(params), headers=headers)
            if is_ok:
                return content['id']
            else:
                self._output('place_order', content)
        except Exception as e:
            print(e)

    def cancel_order(self, symbol: str, entrust_id):
        try:
            url = self.urlbase + f'/orders/{entrust_id}/cancel'
            sign_message = self._sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self._request('PUT', url, headers=headers)
            if is_ok:
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

    def order_detail(self, symbol: str, entrust_id):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/orders/{entrust_id}'
            sign_message = self._sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self._request('GET', url, headers=headers)
            if is_ok:
                results = []
                for order in content['models']:
                    results.append({
                        'status': order['status'],
                        'remaining_amount': float(order['quantity']) - float(order['filled_quantity']),
                        'timestamp': order['create_at'],
                        'price': order['price'],
                        'executed_amount': order['filled_quantity'],
                        'symbol': order['currency_pair_code'],
                        'fees': order['order_fee'],
                        'original_amount': order['quantity'],
                        'entrust_id': order['id'],
                        'side': order['side']
                    })
                return results
            else:
                self._output('order_detail', content)
        except Exception as e:
            print(e)

    def open_orders(self, symbol: str):
        try:
            symbol = self._symbol_convert(symbol)
            url = self.urlbase + f'/orders?product_id={self._product_id(symbol)}'
            sign_message = self._sign_message(url)
            headers = {
                'X-Quoine-API-Version': '2',
                'X-Quoine-Auth': sign_message,
                'Content-Type': 'application/json'
            }
            is_ok, content = self._request('GET', url, headers=headers)
            if is_ok:
                results = []
                for order in content['models']:
                    results.append({
                        'status': order['status'],
                        'remaining_amount': float(order['quantity']) - float(order['filled_quantity']),
                        'timestamp': order['create_at'],
                        'price': order['price'],
                        'executed_amount': order['filled_quantity'],
                        'symbol': order['currency_pair_code'],
                        'fees': order['order_fee'],
                        'original_amount': order['quantity'],
                        'entrust_id': order['id'],
                        'side': order['side']
                    })
                return results
            else:
                self._output('open_orders', content)
        except Exception as e:
            print(e)

    def wallet_balance(self):
        try:
            free, frozen = {}, {}
            for currency in self._get_all_accounts():
                url = self.urlbase + f'/accounts/{currency}'
                sign_message = self._sign_message(url)
                headers = {
                    'X-Quoine-API-Version': '2',
                    'X-Quoine-Auth': sign_message,
                    'Content-Type': 'application/json'
                }
                is_ok, content = self._request('GET', url, headers=headers)
                if is_ok:
                    free[content['currency']], frozen[content['currency']] = content['free_balance'], content['reserved_balance']
            return free, frozen
        except Exception as e:
            print(e)


if __name__ == '__main__':
    quoine = QuoineAuth('https://api.liquid.com', '1672539', "brSxqeetDWhm9GpUFLV9CsoED2d17J91GHy7UEzK+MJpP20WnkHTtA3Q1bvcOsooCo85KkYJmZW8jaLd8NXIuA==")
    # print(quoine.place_order("XRP_BTC", 30, 0.0002, "sell"))
    # order_id = quoine.place_order("XRP_BTC", 30, 0.0002, "sell")
    # print(quoine.cancel_order('XRP_BTC', 1))
    # print(quoine.order_detail('XRP_BTC', 2))
    # print(quoine.open_orders('XRP_BTC'))
    # print(quoine.wallet_balance())

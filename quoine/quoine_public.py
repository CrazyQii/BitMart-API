"""
公共接口
2020-10-4 hlq
"""

import requests
import json


class QuoinePublic:
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def request(self, method, url, params=None, headers=None):
        try:
            if method == 'GET':
                if params is not None:
                    resp = requests.get(url, params=params, headers=headers)
                else:
                    resp = requests.get(url, headers=headers)
            elif method == 'POST':
                resp = requests.post(url, data=json.dumps(params), headers=headers)
            elif method == 'PUT':
                resp = requests.put(url, headers=headers)
            else:
                return False, 'please check method, it does not exist'

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    'status_code': resp.status_code,
                    'method': method,
                    'url': url,
                    'params': params,
                    'resp': resp.text
                }
                return False, error
        except requests.exceptions.RequestException as e:
            print('----- Requests Exception -----')
            error = {
                'method': method,
                'url': url,
                'error_info': e
            }
            return False, error

    def output(self, function_name, content):
        return {
            'function_name': function_name,
            'content': content
        }

    def get_products(self, id: int=None):
        try:
            if id is None:
                url = self.baseurl + '/products'
                is_ok, content = self.request('GET', url)
                if is_ok:
                    products = []
                    for product in content:
                        products.append({
                            'id': product['id'],
                            'product_type': product['product_type'],
                            'code': product['code'],
                            'market_ask': product['market_ask'],
                            'market_bid': product['market_bid'],
                            'currency': product['currency'],
                            'volume_24h': product['volume_24h'],
                            'average_price': product['average_price']
                        })
                    return products
                else:
                    return self.output('get_products', content)
            else:
                url = self.baseurl + f'/products/{id}'
                is_ok, content = self.request('GET', url)
                if is_ok:
                    return content
                else:
                    return self.output('get_products', content)
        except Exception as e:
            return e

    def get_perpetual_products(self, perpetual: int):
        try:
            url = self.baseurl + f'/products?perpetual={perpetual}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                return self.output('get_perpetual_products', content)
        except Exception as e:
            return e

    def get_order_book (self, id: int):
        try:
            url = self.baseurl + f'/products/{id}/price_levels'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                return self.output('get_order_book', content)
        except Exception as e:
            return e

    def get_executions(self, product_id: int, limit: int = None, page: int = None):
        try:
            if limit is None and page is None:
                url = self.baseurl + f'/executions?product_id={product_id}'
            else:
                url = self.baseurl + f'/executions?product_id={product_id}&limit={limit}&page={page}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                return self.output('get_executions', content)
        except Exception as e:
            return e

    def get_interest_rate(self):
        try:
            url = self.baseurl + '/ir_ladders/USD'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                return self.output('get_executions', content)
        except Exception as e:
            return e


if __name__ == '__main__':
    quoine = QuoinePublic('https://api.liquid.com')
    # print(quoine.get_products())
    # print(quoine.get_products(5))
    # print(quoine.get_perpetual_products(1))
    # print(quoine.get_order_book(5))
    # print(quoine.get_executions(5))
    # print(quoine.get_interest_rate())

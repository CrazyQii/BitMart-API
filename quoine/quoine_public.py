"""
公共接口
"""

import requests


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
                resp = requests.post(url, data=params, headers=headers)
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

    def products(self):
        url = self.baseurl + '/products'
        is_ok, content = self.request('GET', url)
        if is_ok:
            products = {
                'id': [i['id'] for i in content if i['id']],
                'product_type': [i['product_type'] for i in content if i['product_type']],
                'code': [i['code'] for i in content if i['code']],
                'market_ask': [i['market_ask'] for i in content if i['market_ask']],
                'market_bid': [i['market_bid'] for i in content if i['market_bid']],
            }
            return products
        else:
            return self.output('products', content)


if __name__ == '__main__':
    quoine = QuoinePublic('https://api.liquid.com')
    print(quoine.products())
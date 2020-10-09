"""
公共接口
2020-10-4 hlq
"""

import requests
import traceback


class QuoinePublic:
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol: str):
        return '-'.join(symbol.split('_'))

    def request(self, method, url, params=None, data=None, headers=None):
        try:
            resp = requests.request(method, url, params=params, data=data, headers=headers)

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    'code': resp.status_code,
                    'method': method,
                    'url': url,
                    'data': data,
                    'msg': resp.text
                }
                return False, error
        except requests.exceptions.RequestException as e:
            error = {
                'method': method,
                'url': url,
                'data': data,
                'traceback': traceback.format_exc(),
                'error': e
            }
            return False, error

    def output(self, function_name, content):
        info = {
            'function_name': function_name,
            'content': content
        }
        print(info)

    def get_products(self, id: int = None):
        try:
            if id is None:
                url = self.urlbase + '/products'
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
                    self.output('get_products', content)
            else:
                url = self.urlbase + f'/products/{id}'
                is_ok, content = self.request('GET', url)
                if is_ok:
                    return content
                else:
                    self.output('get_products', content)
        except Exception as e:
            print(e)

    def get_perpetual_products(self, perpetual: int):
        try:
            url = self.urlbase + f'/products?perpetual={perpetual}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                self.output('get_perpetual_products', content)
        except Exception as e:
            print(e)

    def get_orderbook(self, id: int):
        try:
            url = self.urlbase + f'/products/{id}/price_levels'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                self.output('get_orderbook', content)
        except Exception as e:
            print(e)

    def get_executions(self, product_id: int, limit: int = None, page: int = None):
        try:
            if limit is None and page is None:
                url = self.urlbase + f'/executions?product_id={product_id}'
            else:
                url = self.urlbase + f'/executions?product_id={product_id}&limit={limit}&page={page}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                self.output('get_executions', content)
        except Exception as e:
            print(e)

    def get_interest_rate(self):
        try:
            url = self.urlbase + '/ir_ladders/USD'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content
            else:
                return self.output('get_executions', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    quoine = QuoinePublic('https://api.liquid.com')
    # print(quoine.get_products())
    # print(quoine.get_products(5))
    # print(quoine.get_perpetual_products(1))
    # print(quoine.get_orderbook(5))
    # print(quoine.get_executions(5))
    # print(quoine.get_interest_rate())

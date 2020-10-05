"""
公共接口
2020-9-28 hlq
"""
import requests


class HooPublic:
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
                return False, 'check method, it is not exist'
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

    def get_tickers_market(self):
        try:
            url = self.baseurl + '/open/v1/tickers/market'
            is_ok, content = self.request('GET', url)
            if is_ok:
                data = content['data']
                tickers = {
                    'amount': [float(i['amount']) for i in data if i['amount']],
                    'amt_num': [[int(i['amt_num']) for i in data if i['amt_num']]],
                    'change': [float(i['change']) for i in data if i['change']],
                    'high': [float(i['high']) for i in data if i['high']],
                    'low': [float(i['low']) for i in data if i['low']],
                    'price': [float(i['price']) for i in data if i['price']],
                    'qty_num': [[int(i['qty_num']) for i in data if i['qty_num']]],
                    'symbol': [i['symbol'] for i in data if i['symbol']],
                    'volume': [float(i['volume']) for i in data if i['volume']]
                }
                return tickers
            else:
                return self.output('get_tickers_market', content)
        except Exception as e:
            return e


if __name__ == '__main__':
    hoo = HooPublic('https://api.hoolgd.com')
    # print(hoo.get_tickers_market())

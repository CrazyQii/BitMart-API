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
                return content['data']
            else:
                return self.output('get_tickers_market', content)
        except Exception as e:
            return e

    def get_depth(self, symbol: str):
        try:
            url = self.baseurl + f'/open/v1/depth/market?symbol={symbol}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                result = {
                    'bids': [],
                    'asks': []
                }
                for item in content['data']['bids']:
                    result['bids'].append([float(item['price']), float(item['quantity'])])
                for item in content['data']['asks']:
                    result['asks'].append([float(item['price']), float(item['quantity'])])
                return result
            else:
                return self.output('get_depth', content)
        except Exception as e:
            return e

    def get_trades(self, symbol: str):
        try:
            url = self.baseurl + f'/open/v1/trade/market?symbol={symbol}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content['data']
            else:
                return self.output('get_trades', content)
        except Exception as e:
            return e

    def get_kline(self, symbol: str, type: str):
        try:
            url = self.baseurl + f'/open/v1/kline/market?symbol={symbol}&type={type}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content['data']
            else:
                return self.output('get_trades', content)
        except Exception as e:
            return e


if __name__ == '__main__':
    hoo = HooPublic('https://api.hoolgd.com')
    # print(hoo.get_tickers_market())
    # print(hoo.get_depth('BTC-USDT'))
    # print(hoo.get_trades('BTC-USDT'))
    print(hoo.get_kline('BTC-USDT', '1Min'))
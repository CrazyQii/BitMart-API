"""
公共接口
2020-9-28 hlq
"""
import requests
import traceback


class HooPublic:
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

    def get_tickers_market(self):
        try:
            url = self.urlbase + '/open/v1/tickers/market'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content['data']
            else:
                self.output('get_tickers_market', content)
        except Exception as e:
            print(e)

    def get_depth(self, symbol: str):
        try:
            url = self.urlbase + f'/open/v1/depth/market?symbol={self.symbol_convert(symbol)}'
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
                self.output('get_depth', content)
        except Exception as e:
            print(e)

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f'/open/v1/trade/market?symbol={self.symbol_convert(symbol)}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content['data']
            else:
                self.output('get_trades', content)
        except Exception as e:
            print(e)

    def get_kline(self, symbol: str, type: str):
        try:
            url = self.urlbase + f'/open/v1/kline/market?symbol={self.symbol_convert(symbol)}&type={type}'
            is_ok, content = self.request('GET', url)
            if is_ok:
                return content['data']
            else:
                self.output('get_trades', content)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    hoo = HooPublic('https://api.hoolgd.com')
    # print(hoo.get_tickers_market())
    # print(hoo.get_depth('BTC_USDT'))
    # print(hoo.get_trades('BTC_USDT'))
    # print(hoo.get_kline('BTC_USDT', '1Min'))
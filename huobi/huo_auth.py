"""
HuoBi authentication api
2020/10/13 hlq
"""

from huobi.huo_public import HuoPublic
import datetime


class HuoAuth(HuoPublic):
    def __init__(self, urlbase, api_key, api_secret):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret

    def _get_timestamp(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    def _sign_message(self, method, host, path, params):
        req_str = ['&'.join(f'{key}={value}') for key, value in params]

        payload = f'{method}\n{host}\n{path}\n{req_str}'
        print(payload)


if __name__ == '__main__':
    huo = HuoAuth('https://api.huobi.pro', '868328f5-dqnh6tvdf3-60a6530c-31675', '115158e5-d91ecf17-b53fa082-fcdd8')

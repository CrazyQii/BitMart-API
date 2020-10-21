class KucoinAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase=None):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret
        self.memo = passphrase

    def _sign_message(self, params):
        pass

    def place_order(self, symbol: str, amount: float, price: float, side: str):
        pass

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
    ku = KucoinAuth('', '5f8ebf0814f0ab000626b75d',
                      '410aacfb-8e1d-433b-86e9-2a02b96a0794')
    # print(ku.place_order('EOS_USDT', 1.0016, 11, 'buy'))
    # print(ku.order_detail('BTC_USDT', '1'))
    # print(ku.open_orders('BTC_USDT'))
    # print(ku.cancel_order('UMA_USDT', '1'))
    # print(ku.cancel_all('BTC_USDT', 'buy'))
    # print(ku.wallet_balance())
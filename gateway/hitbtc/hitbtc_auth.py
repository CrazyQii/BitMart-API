class HitbtcAuth(object):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
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
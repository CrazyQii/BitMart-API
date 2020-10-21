class HitbtcPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _load_symbols_info(self):
        pass

    def get_symbol_info(self, symbol: str):
        pass

    def get_price(self, symbol: str):
        pass

    def get_ticker(self, symbol: str):
        pass

    def get_orderbook(self, symbol: str):
        pass

    def get_trades(self, symbol: str):
        pass

    def get_kline(self, symbol: str, time_period=3000, interval=1):
        pass


if __name__ == '__main__':

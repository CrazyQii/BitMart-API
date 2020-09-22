"""
bitmart_api.py
-------------------
api接口文件
"""
from . import client, const as c


class API:
    def __init__(self, api_key, secret_key, memo):
        self.clients = client.Client(api_key=api_key, secret_key=secret_key, memo=memo)

    # GET https://api-cloud.bitmart.com/spot/v1/currencies
    def get_currencies(self):
        return self.clients.request_without_param('GET', c.API_SPOT_CURRENCIES_URL)

    # GET https://api-cloud.bitmart.com/spot/v1/symbols
    def get_symbols(self):
        return self.clients.request_without_param('GET', c.API_SPOT_SYMBOLS_URL)

    # GET https://api-cloud.bitmart.com/spot/v1/symbols/details
    def get_symbols_detail(self):
        return self.clients.request_without_param('GET', c.API_SPOT_SYMBOLS_DETAILS_URL)

    # GET https://api-cloud.bitmart.com/spot/v1/ticker
    def get_tickers(self, symbol: str):
        return self.clients.request_with_param('GET', c.API_SPOT_TICKER_URL, {'symbol':  symbol})

    # GET https://api-cloud.bitmart.com/spot/v1/steps
    def get_steps(self):
        return self.clients.request_without_param('GET', c.API_SPOT_STEPS_URL)

    # GET https://api-cloud.bitmart.com/spot/v1/symbols/kline
    def get_symbol_kline(self, symbol: str, step: int, fromTime: int, toTime: int):
        param = {
            'symbol': symbol,
            'step': step,
            'from': fromTime,
            'to': toTime
        }
        return self.clients.request_with_param('GET', c.API_SPOT_SYMBOLS_KLINE_URL, param)

    # GET https://api-cloud.bitmart.com/spot/v1/symbols/book
    def get_symbol_book(self, symbol: str, precision: int):
        param = {
            'symbol': symbol,
            'precision': precision
        }
        return self.clients.request_with_param('GET', c.API_SPOT_SYMBOLS_BOOK_URL, param)

    # GET https://api-cloud.bitmart.com/spot/v1/symbols/trades
    def get_symbol_trade(self, symbol: str):
        return self.clients.request_with_param('GET', c.API_SPOT_SYMBOLS_BOOK_URL, {'symbol': symbol})

    # GET https://api-cloud.bitmart.com/spot/v1/wallet
    def get_wallet(self):
        return self.clients.request_without_param('GET', c.API_SPOT_WALLET_URL, c.AUTH_KEYED)

    # POST https://api-cloud.bitmart.com/spot/v1/submit_order
    def post_limit_submit_order(self, symbol: str, side: str, size='', price=''):
        param = {
            'symbol': symbol,
            'side': side,
            'type': 'limit',
            'size': size,
            'price': price
        }
        return self.clients.request_with_param('POST', c.API_SPOT_SUBMIT_ORDER_URL, param, c.AUTH_SIGN)

    def post_market_submit_order(self, symbol: str, side: str, size='', notional=''):
        param = {
            'symbol': symbol,
            'side': side,
            'type': 'market',
            'size': size,
            'notional': notional
        }
        return self.clients.request_with_param('POST', c.API_SPOT_SUBMIT_ORDER_URL, param, c.AUTH_SIGN)

    # POST https://api-cloud.bitmart.com/spot/v1/cancel_order
    def post_cancel_order(self, symbol: str, order_id=''):
        param = {
            'symbol': symbol,
            'order_id': order_id
        }
        return self.clients.request_with_param('POST', c.API_SPOT_CANCEL_ORDER_URL, param, c.AUTH_SIGN)

    # POST https://api-cloud.bitmart.com/spot/v1/cancel_orders
    def post_cancel_orders(self, symbol: str, side=''):
        param = {
            'symbol': symbol,
            'side': side
        }
        return self.clients.request_with_param('POST', c.API_SPOT_CANCEL_ORDERS_URL, param, c.AUTH_SIGN)

    # GET https://api-cloud.bitmart.com/spot/v1/order_detail
    def get_order_detail(self, symbol: str, order_id=''):
        param = {
            'symbol': symbol,
            'order_id': order_id
        }
        return self.clients.request_with_param('GET', c.API_SPOT_ORDER_DETAIL_URL, param, c.AUTH_KEYED)

    # GET https://api-cloud.bitmart.com/spot/v1/orders
    def get_orders(self, symbol: str, status: int, offset: int, limit: int):
        param = {
            'symbol': symbol,
            'status': status,
            'offset': offset,
            'limit': limit
        }
        return self.clients.request_with_param('GET', c.API_SPOT_ORDERS_URL, param, c.AUTH_KEYED)

    # GET https://api-cloud.bitmart.com/spot/v1/trades
    def get_trades(self, symbol: str, limit: int, offset: int):
        param = {
            'symbol': symbol,
            'offset': offset,
            'limit': limit
        }
        return self.clients.request_with_param('GET', c.API_SPOT_TRADES_URL, param, c.AUTH_KEYED)

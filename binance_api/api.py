"""
api.py
----------
api接口文件
"""
from binance_api import api_client, api_util
from binance_api.api_const import *
from binance_api.api_parse_params import *


class API:
    def __init__(self, api_key, secret_key):
        self.clients = api_client.Client(api_key, secret_key)

    # GET https://api.binance.com/api/v3/ping
    def get_ping(self):
        return self.clients.request_without_param(GET, API_PING_URL, AUTH_NONE, 1)

    # GET https://api.binance.com/api/v3/exchangeInfo
    def get_exchange_info(self):
        return self.clients.request_without_param(GET, API_EXCHANGE_INFO_URL, AUTH_NONE, 1)

    # POST https://api.binance.com/api/v3/order
    def post_order(self, symbol: str, side: str, type: str, time_in_force=None,
                   quantity=None, quote_order_Qty=None, price=None, new_client_order_id=None,
                   stop_price=None, iceberg_Qty=None, recv_window=5000):
        # 公共参数
        com_param = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'newClientOrderId': api_util.get_new_client_order_id(new_client_order_id),  # 生成用户自定义订单id
            'recvWindow': recv_window
        }
        # 逻辑处理对应不同 type 请求参数
        if type == LIMIT:
            pri_param = parse_LIMIT_order(time_in_force, quantity, price, FULL)
        elif type == LIMIT and iceberg_Qty is not None:
            pri_param = parse_LIMIT_ICEBERG_order(GTC, quantity, price, iceberg_Qty, FULL)
        elif type == MARKET:
            pri_param = parse_MARKET_order(quantity, quote_order_Qty, FULL)
        elif type == STOP_LOSS:
            pri_param = parse_STOP_LOSS_order(quantity, stop_price, ACK)
        elif type == STOP_LOSS_LIMIT:
            pri_param = parse_STOP_LOSS_LIMIT_order(time_in_force, quantity, stop_price, price, ACK)
        elif type == TAKE_PROFIT:
            pri_param = parse_TAKE_PROFIT_order(quantity, stop_price, new_client_order_id)
        elif type == TAKE_PROFIT_LIMIT:
            pri_param = parse_TAKE_PROFIT_LIMIT_order(time_in_force, quantity, stop_price, price, ACK)
        elif type == LIMIT_MAKER:
            pri_param = parse_LIMIT_MAKER_order(quantity, price, new_client_order_id)
        else:
            pri_param = {}
        param = dict(com_param, **pri_param)

        return self.clients.request_with_param(POST, API_ORDER_URL, param, AUTH_TYPE_TRADE, weight=1)

    # DELETE https://api.binance.com/api/v3/order
    def delete_order(self, symbol: str, order_id, orig_client_order_id, new_client_order_id=None, recv_window=5000):
        if order_id is not None:
            param = {
                'symbol': symbol,
                'orderId': order_id,
                'newClientOrderId': api_util.get_new_client_order_id(new_client_order_id),  # 生成用户自定义订单id
                'recvWindow': recv_window
            }
        else:
            param = {
                'symbol': symbol,
                'origClientOrderId': orig_client_order_id,
                'newClientOrderId': api_util.get_new_client_order_id(new_client_order_id),  # 生成用户自定义订单id
                'recvWindow': recv_window
            }
        return self.clients.request_with_param(DELETE, API_ORDER_URL, param, AUTH_TYPE_TRADE, weight=1)

    # DELETE https://api.binance.com/api/v3/openOrders
    def delete_open_order(self, symbol: str, recv_window=5000):
        param = {
            'symbol': symbol,
            'recvWindow': recv_window
        }
        return self.clients.request_with_param(DELETE, API_OPEN_ORDER_URL, param, AUTH_TYPE_TRADE, weight=1)

    # GET https://api.binance.com/api/v3/order
    def get_order(self, symbol: str, order_id, orig_client_order_id,  recv_window=5000):
        if order_id is not None:
            param = {
                'symbol': symbol,
                'orderId': order_id,
                'recvWindow': recv_window
            }
        else:
            param = {
                'symbol': symbol,
                'origClientOrderId': orig_client_order_id,
                'recvWindow': recv_window
            }
        return self.clients.request_with_param(GET, API_ORDER_URL, param, AUTH_TYPE_USER_DATA, weight=1)

    # GET https://api.binance.com/api/v3/openOrders
    def get_open_order(self, symbol: str, recv_window=5000):
        param = {
            'symbol': symbol,
            'recvWindow': recv_window
        }
        return self.clients.request_with_param(GET, API_OPEN_ORDER_URL, param, AUTH_TYPE_TRADE, weight=1)

    # 存在问题
    # GET https://api.binance.com/api/v3/allOrders
    def get_all_order(self, symbol: str, order_id=None, start_time=None, end_time=None, limit=None, recv_window=5000):
        param = {
            'symbol': symbol,

            'recvWindow': recv_window
        }
        return self.clients.request_with_param(GET, API_OPEN_ORDER_URL, param, AUTH_TYPE_TRADE, weight=5)

    # 存在问题
    # GET https://api.binance.com/api/v3/myTrades
    def get_my_trades(self, start_time=None, end_time=None, from_id=None, limit=None, recv_window=5000):
        param = {
            'recvWindow': recv_window
        }
        return self.clients.request_with_param(GET, API_MY_TRADES_URL, param, AUTH_TYPE_USER_DATA, weight=5)

    # GET https://api.binance.com/api/v3/account
    def get_account(self, recv_window=5000):
        param = {
            'recvWindow': recv_window
        }
        return self.clients.request_with_param(GET, API_ACCOUNT_URL, param, AUTH_TYPE_USER_DATA, weight=1)

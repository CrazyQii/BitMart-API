"""
api.py
----------
api接口文件
"""
from binance_api import client, util, const as c
from enum import Enum


class API:
    def __init__(self, api_key, secret_key):
        self.clients = client.Client(api_key, secret_key)

    # POST https://api.binance.com/api/v3/order/test
    def post_limit_order_test(self, symbol: str, side: Enum, time_in_force: Enum,
                              quantity: float, price: float, new_client_order_id=None,
                              new_order_resp_type=c.NewOrderRespType.FULL.value,
                              recv_window=5000):

        param = {
            'symbol': symbol,
            'side': side,
            'type': c.OrderTypes.LIMIT.value,
            'timeInForce': time_in_force,
            'quantity': quantity,
            'price': price,
            'newClientOrderId': util.get_new_client_order_id(new_client_order_id),  # 生成用户自定义订单id
            'newOrderRespType': new_order_resp_type,
            'recv_window': recv_window,
        }
        return self.clients.request_with_param(c.POST, c.API_ORDER_TEST_URL, param, c.AUTH_TYPE_TRADE, weight=1)

    def post_limit_order_test_with_iceberg(self, symbol: str, side: Enum, quantity: float,
                                           price: float, icebergQty: float, new_client_order_id=None,
                                           new_order_resp_type=c.NewOrderRespType.FULL.value,
                                           recv_window=5000):
        param = {
            'symbol': symbol,
            'side': side,
            'type': c.OrderTypes.LIMIT.value,
            'timeInForce': c.TimeInForce.GTC.value,
            'quantity': quantity,
            'price': price,
            'icebergQty': icebergQty,
            'newClientOrderId': util.get_new_client_order_id(new_client_order_id),
            'newOrderRespType': new_order_resp_type,
            'recv_window': recv_window,
        }
        return self.clients.request_with_param(c.POST, c.API_ORDER_TEST_URL, param, c.AUTH_TYPE_TRADE, weight=1)

    # def post_market_order_test(self, symbol: str, side: Enum, quantity: float, quote_order_qty: float, recv_window=5000):
    #     param = {
    #         'symbol': symbol,
    #         'side': str(side),
    #         'type': 'market',
    #         'timeInForce': str(time_in_force),
    #         'quantity': quantity,
    #         'price': price,
    #         'recv_window': recv_window
    #     }
    #     return self.clients.request_with_param(c.POST, c.ORDER_TEST, param, c.AUTH_TYPE_TRADE)
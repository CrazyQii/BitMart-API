"""
api_parse_params.py
----------------------
解析请求参数，根据不同 type 构造不同参数
"""


# POST https://api.binance.com/api/v3/order/test
# POST https://api.binance.com/api/v3/order/
def parse_LIMIT_order(time_in_force: str, quantity: float,  price: float, new_order_resp_type: str):
    param = {
        'timeInForce': time_in_force,
        'quantity': quantity,
        'price': price,
        'newOrderRespType': new_order_resp_type
    }
    return param


def parse_LIMIT_ICEBERG_order(time_in_force: str, quantity: float,  price: float, iceberg_Qty: float, new_order_resp_type: str):
    param = {
        'timeInForce': time_in_force,
        'quantity': quantity,
        'price': price,
        'icebergQty': iceberg_Qty,
        'newOrderRespType': new_order_resp_type
    }
    return param


def parse_MARKET_order(quantity: float, quote_order_Qty: float, new_order_resp_type: str):
    if quantity is not None:
        param = {
            'quantity': quantity,
            'newOrderRespType': new_order_resp_type
        }
        return param
    else:
        param = {
            'quoteOrderQty': quote_order_Qty,
            'newOrderRespType': new_order_resp_type
        }
        return param


def parse_STOP_LOSS_order(quantity: float, stop_price: float, new_order_resp_type: str):
    param = {
        'quantity': quantity,
        'stopPrice': stop_price,
        'newOrderRespType': new_order_resp_type
    }
    return param


def parse_STOP_LOSS_LIMIT_order(time_in_force: str, quantity: float, stop_price: float, price: float, new_order_resp_type: str):
    param = {
        'timeInForce': time_in_force,
        'quantity': quantity,
        'stopPrice': stop_price,
        'price': price,
        'newOrderRespType': new_order_resp_type
    }
    return param


def parse_TAKE_PROFIT_order(quantity: float, stop_price: float, new_order_resp_type: str):
    param = {
        'quantity': quantity,
        'stopPrice': stop_price,
        'newOrderRespType': new_order_resp_type
    }
    return param


def parse_TAKE_PROFIT_LIMIT_order(time_in_force: str, quantity: float, stop_price: float, price: float, new_order_resp_type: str):
    param = {
        'timeInForce': time_in_force,
        'quantity': quantity,
        'stopPrice': stop_price,
        'price': price,
        'newOrderRespType': new_order_resp_type
    }
    return param


def parse_LIMIT_MAKER_order(quantity: float, price: float, new_order_resp_type: str):
    param = {
        'quantity': quantity,
        'price': price,
        'newOrderRespType': new_order_resp_type
    }
    return param

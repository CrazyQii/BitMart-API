"""
const.py
-----------------
常量
"""
from enum import Enum, unique

# User
USER_API_KEY = 'peHvRKu7QGVZIezAlZfIAhmK5zPxa5ptLo6kkMOLGeJpD1UJhpufUVY6WvYqrDrh'
USER_SECRET_KEY = 'GS6Us3YWMw7sQQMEm5uC90CrgFcvtSOlGyz3PzWA5KXsUamYG4Y4ieqW6oziKZ72'

BASE_URL = 'https://api.binance.com'

# Headers
CONTENT_TYPE = 'Content-type'
USER_AGENT = 'User-Agent'
X_MBX_APIKEY = 'X-MBX-APIKEY'
X_MBX_WEIGHT = 'X-MBX-WIGHT'
APPLICATION_JSON = 'application/json'
VERSION = 'HanLQ-Bitmart-API/1.0.1'

# method
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# authentication
AUTH_NONE = None
AUTH_KEYED = 'keyed'
AUTH_KEYED_AND_SIGNED = 'keyed_signed'

# authentication type
AUTH_TYPE_TRADE = 'keyed_signed'
AUTH_TYPE_USER_DATA = 'keyed_signed'
AUTH_TYPE_USER_STREAM = 'keyed'
AUTH_TYPE_MARKET_DATA = 'keyed'

# request_url
API_ORDER_TEST_URL = '/api/v3/order/test'  # 测试下单
API_ORDER_URL = '/api/v3/order'  # 下单


@unique
class OrderTypes(Enum):
    """ 订单类型 """
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    LIMIT_MAKER = 'LIMIT_MAKER'


@unique
class NewOrderRespType(Enum):
    """ 订单返回类型 """
    ACK = 'ACK'
    RESULT = 'RESULT'
    FULL = 'FULL'


@unique
class Side(Enum):
    """ 订单方向 """
    BUY = 'BUY'
    SELL = 'SELL'


@unique
class TimeInForce(Enum):
    """ 有效方式 """
    GTC = 'GTC'
    IOC = 'IOC'
    FOK = 'FOK'


@unique
class IntervalLetter(Enum):
    """access limitation"""
    SECOND = 'S'
    MINUTE = 'M'
    HOUR = 'H'
    DAY = 'D'

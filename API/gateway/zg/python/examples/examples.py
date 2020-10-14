from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import logging
import time

from broker.client import BrokerClient

if __name__ == '__main__':
    from broker import broker_log

    broker_log.setLevel(logging.DEBUG)
    broker_log.addHandler(logging.StreamHandler())

    proxies = {
        "http": "",
        "https": "",
    }
    api_key= '26lgbEfY4eeVXFX9U81GbLQIWrPoej10PKe80r7UQSeKANtZDsFn2h03P81nbnfW' #"fONXv5tzp4sguTNbons2YcwmE8sZCHoMKuDCnZbRekdB3REMqRZ0f8Nj93uYpZlZ"
    api_secret= 'E8dL7PtMUY8yfPsa0UqrPfqkYrmv3UhzjdiOn3EFH2SDqHzSDF1E0IKKZhPZn3IX' #"CIbyLoeBRyAVeJkqDT4sAGCkioKszVuZedOlIn8USegGuJkNQbie1H7FMkdx8pXj"
    entry_point = 'https://api.zg.com'  # like: https://api.xxx.yyy/openapi/ where xxx.yyy is your base domain
    b = BrokerClient(entry_point, api_key=api_key, secret=api_secret, proxies=proxies)

    # print(b.time())

    # print(int(time.time() * 1000))

    # print(b.broker_info())

    # print(b.depth('BTCUSDT'))

    # print(b.trades('BTCUSDT'))

    # print(b.klines('BTCUSDT'))

    # print(b.ticker_24hr('BTCUSDT'))

    # result = b.order_new(symbol='BTCUSDT', side='BUY', type='LIMIT', quantity='0.1', price='6000', timeInForce='GTC')

    # print(result)

    # order_id = result['orderId']

    # print(order_id)

    # print(b.order_get(order_id=order_id))

    # print(b.order_cancel(order_id=order_id))

    # print(b.open_orders())

    # print(b.history_orders())

    print(b.account())

    print(b.my_trades())

    listen_key = b.stream_get_listen_key()

    print(listen_key)

    print(b.stream_keepalive(listen_key.get('listenKey')))

    print(b.stream_close(listen_key.get('listenKey')))

    print(b.deposit_orders())

from threading import Thread
import redis
import json
import time


class Client(Thread):
    def __init__(self):
        super().__init__()
        self.server = redis.StrictRedis(host='localhost', port=6379)
        self.start_time = None

    def subscribe(self, gateway, symbol, feature):
        try:
            channel = f'{gateway}&{symbol}&{feature}'
            # 存入redis数据库，通知发布者开启订阅订阅通道
            params = [channel]
            self.server.set('sub', json.dumps(params))
            # 订阅频道
            pub = self.server.pubsub()
            pub.subscribe(json.dumps(channel))

            error_time = 0
            for recv in pub.listen():
                if error_time > 10000:
                    return
                if recv['type'] == 'message':
                    data = json.loads(recv['data'])
                    if data['code'] == 200:
                        error_time = 0
                        yield data
                    elif data['code'] == 403:
                        error_time += 1
                    else:
                        error_time += 1
                else:
                    print(recv)
        except Exception as e:
            print(f'client subscribe error: {e}')

    def receiver(self, symbol, feature, gateway=None):
        try:
            if gateway is None:
                for gateway in ['binance', 'okex', 'huobi', 'wootrade']:
                    for data in self.subscribe(gateway, symbol, feature):
                        yield data
            elif isinstance(gateway, list):
                for gateway in gateway:
                    for data in self.subscribe(gateway, symbol, feature):
                        yield data
            elif isinstance(gateway, str):
                for data in self.subscribe(gateway, symbol, feature):
                    yield data
            else:
                raise Exception('Args format error!!')
        except Exception as e:
            print(f'Receiver error: {e}')


client = Client()

# if __name__ == '__main__':
#     client = Client()
#     for i in client.receiver('BTC_USDT', 'price'):
#         print(i)

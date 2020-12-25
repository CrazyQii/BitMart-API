import redis
import json

r = redis.StrictRedis(host='localhost', port=6379)
# 存入redis数据库，通知发布者开启订阅订阅通道
params = ['huobi&OXT_USDT&price']
r.set('sub', json.dumps(params))

# 开始订阅
p1 = r.pubsub()

# channel = 'binance&BTC_USDT&trade'
# p1.subscribe(json.dumps(channel))
#
# channel = 'binance&BTC_USDT&kline'
# p1.subscribe(json.dumps(channel))

channel = 'huobi&OXT_USDT&price'
p1.subscribe(json.dumps(channel))

# channel = 'binance&BTC_USDT&orderbook'
# p1.subscribe(json.dumps(channel))

def lit():
    for message in p1.listen():
        yield message

for i in lit():
    print(i)



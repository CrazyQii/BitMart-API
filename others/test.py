from others.client import client
for item in client.receiver('BTC_USDT', 'orderbook', 'wootrade'):
    print(item)
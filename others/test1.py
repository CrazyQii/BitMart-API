from others.client import client
for item in client.receiver('BTC_USDT', 'orderbook', 'okex'):
    print(item)
from gateway.binance.binance_websocket import BinanceWs
from gateway.okex.okex_websocket import OkexWs
from gateway.huobi.huobi_websocket import HuobiWs
from gateway.wootrade.wootrade_websocket import WootradeWs
from threading import Thread
from cacheout import Cache
import redis                    
import time
import json
import logging


class Gateway(Thread):
    def __init__(self):
        super().__init__()
        self.channels = []
        self.gateways = {'binance': BinanceWs, 'okex': OkexWs, 'huobi': HuobiWs, 'wootrade': WootradeWs}
        self.ongoing_gateway = {}
        self.feature = ['price', 'orderbook', 'trade', 'kline', 'order', 'wallet']
        self.cache = Cache(maxsize=256, timer=time.time)
        self.server = redis.StrictRedis(host='localhost', port=6379)
        logging.basicConfig()
        Thread(target=self.receiver).start()
        Thread(target=self.publisher).start()

    def _integrate_gateway(self, gateway, symbol: str, feature: str):
        try:
            switch = {
                'price': gateway.sub_price,
                'orderbook': gateway.sub_orderbook,
                'trade': gateway.sub_trade,
                'kline': gateway.sub_kline,
                'order': gateway.sub_order,
                'wallet': gateway.sub_wallet_balance
            }
            switch.get(feature, lambda r: print(f'{feature} feature dose not exist!'))(symbol)
        except Exception as e:
            print(f'Integrate gateway error: {e}')

    def _handle_receiver(self):
        try:
            recv = self.server.get('sub')
            if recv:
                recv = json.loads(recv)
                # print(recv)
                for item in recv:
                    if item not in self.channels:
                        gateway, symbol, feature = item.split('&')
                        # 操作数据
                        # 1. 判断交易所是否存在，若不存在返回错误，若存在，实例化交易所
                        if gateway in self.gateways:
                            # 2. 判断交易所是否已经实例化过
                            if gateway not in self.ongoing_gateway:
                                instant_gate = self.gateways[gateway]()
                                self.ongoing_gateway.update({
                                    gateway: instant_gate
                                })
                            self._integrate_gateway(self.ongoing_gateway[gateway], symbol, feature)
                            self.channels.append(item)
                        else:
                            msg = f'{gateway} does not exist'
                            data = {
                                'code': 500,
                                'data': None,
                                'msg': msg
                            }
                            self.server.publish(channel=json.dumps(recv), message=json.dumps(data))
                self.server.delete('sub')
        except Exception as e:
            print(f'Receiver error {e}')

    def receiver(self):
        try:
            while True:
                time.sleep(2)
                # 订阅者发送订阅请求
                if self.server.exists('sub'):
                    self._handle_receiver()
        except Exception as e:
            print(f'Receiver error: {e}')

    def publisher(self):
        try:
            while True:
                time.sleep(0.001)
                for channel in self.channels:
                    gateway, symbol, feature = channel.split('&')
                    data = self.ongoing_gateway[gateway].data[symbol][feature]
                    print(data)
                    # 币对不存在，服务器错误
                    if data is None or len(data) == 0:
                        data = f'{gateway}&{symbol}&{feature} does not exist'
                    # 设置缓存，判断数据是否重复
                    cache_data = self.cache.get(f'{gateway}&{symbol}&{feature}')
                    if cache_data is None:
                        # 缓存数据不存在，更新缓存数据，有效期为15秒
                        if feature == 'kline' and len(data) > 0:
                            self.cache.set(f'{gateway}&{symbol}&{feature}', data[0], ttl=15)
                        else:
                            self.cache.set(f'{gateway}&{symbol}&{feature}', data, ttl=15)
                    else:
                        if data == cache_data:  # trade / orderbook / price
                            data = {
                                'code': 403,
                                'data': data,
                                'msg': 'Duplicate Data'
                            }
                            self.server.publish(channel=json.dumps(channel), message=json.dumps(data))
                            continue
                        elif type(data) == list and data[0] == cache_data:  # kline
                            data = {
                                'code': 403,
                                'data': data,
                                'msg': 'Duplicate Data'
                            }
                            self.server.publish(channel=json.dumps(channel), message=json.dumps(data))
                        else:  # 新数据与缓存中的数据不同，更新数据
                            if feature == 'kline' and len(data) > 0:
                                self.cache.set(f'{gateway}&{symbol}&{feature}', data[0], ttl=15)
                            else:
                                self.cache.set(f'{gateway}&{symbol}&{feature}', data, ttl=15)
                            data = {
                                'code': 200,
                                'data': data,
                                'msg': 'OK'
                            }
                            self.server.publish(channel=json.dumps(channel), message=json.dumps(data))
        except Exception as e:
            print(f'Publisher error: {e}')


if __name__ == '__main__':
    g = Gateway()

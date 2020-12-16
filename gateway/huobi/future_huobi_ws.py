import websocket
import gzip
import json
import threading
import time
import logging

class HuobiDMWs(threading.Thread):

    # 订阅 KLine 数据
    tradeStr_kline = json.dumps({"sub": "market.BTC_CQ.kline.1min",  "id": "id1"})
    
    # 订阅 Market Detail 数据
    tradeStr_marketDetail = json.dumps({"sub": "market.BTC_CQ.detail",  "id": "id6" })

    # 订阅 Trade Detail 数据
    tradeStr_tradeDetail=json.dumps({"sub": "market.BTC_CQ.trade.detail", "id": "id7"})

    # 请求 KLine 数据
    tradeStr_klinereq=json.dumps({"req": "market.BTC_CQ.kline.1min", "id": "id4"})

    # 请求 Trade Detail 数据
    tradeStr_tradeDetail_req=json.dumps({"req": "market.BTC_CQ.trade.detail", "id": "id5"})

    # 订阅 Market Depth 数据
    tradeStr_marketDepth=json.dumps({"sub": "market.BTC_CQ.depth.step0", "id": "id9"})


    def __init__(self,channels=None,url=None):
        super().__init__()

        if url is None:
            self.url = "wss://api.hbdm.com/ws"
        else:
            self.url = url

        if channels is None:
            self.channels = [self.tradeStr_marketDepth]
        elif isinstance(channels,str):
            self.channels = [channels]
        else:
            self.channels = channels


        self.logger = logging.getLogger()
        self.name = "HuobiDMWs"

        # self.ticker = dict()
        # self.trade = dict()
        # self.depth = dict()
        # self.kline = dict()

        self.init_container()
        self.ws = None

        self.depth_level = 10
        self.reconect_counts = 0
        self.last_open_time = 0

    def get_instrument(self,channel):
        if "depth" in channel:
            return channel.split(".")[1]
        else:
            return channel


    def init_container(self):
        self.ticker = dict()
        self.trade = dict()
        self.depth = dict()
        self.kline = dict()
        self.index = dict()
        self.basis = dict()

    def on_message(self, message):
        message = self.inflate(message)
        channel = message.get("ch","")

        if "ping" in message:
            self.response_pong(message)
        elif "depth" in channel:
            '''
            >> message.keys()
            dict_keys(['ch', 'ts', 'tick'])
            >> message["tick"].keys()
            dict_keys(['mrid', 'id', 'bids', 'asks', 'ts', 'version', 'ch'])
            '''
            self.depth[channel] = message["tick"]
            #     "asks":message["tick"]["asks"][:self.depth_level],
            #     "bids":message["tick"]["bids"][:self.depth_level]
            # }

        elif "trade.detail" in channel:
            '''
            >> message.keys()
            dict_keys(['ch', 'ts', 'tick'])

            >> message["tick"].keys()
            dict_keys(['id', 'ts', 'data'])

            >> message["tick"]["data"][0].keys()
            dict_keys(['amount', 'ts', 'id', 'price', 'direction'])
            '''
            self.trade[channel] = message["tick"]["data"]
        elif "index" in channel:
            self.index[channel] = message["tick"]

        elif "basis" in channel:
            self.basis[channel] = message["tick"]

        else:
            ustring = f"unexpected data:{message}"
            self.logger.info(ustring)
    

    def on_error(self, error):
        try:
            error = self.inflate(error)
            self.logger.info("### hb websocket on_error ###")
            self.logger.info(error)
        except:
            self.logger.exception("hb websocket on_error")

    def on_close(self):
        self.ws = None
        self.logger.info("### hb websocket on_close ###")

    def on_open(self):
        self.logger.info("### hb websocket on_open ###")
        self.last_open_time = time.time()
        length = len(self.channels)
        for ch in self.channels:
            _id = self.get_instrument(ch)
            ch = {
                "sub": ch, 
                "id": _id
            }
            self.ws.send(json.dumps(ch))
            if length > 20:
                time.sleep(0.1)

    def response_pong(self, msg):
        data = {"pong": msg['ping']}
        self.ws.send(json.dumps(data))

    def inflate(self,data):

        strdata = gzip.decompress(data).decode('utf-8')
        return json.loads(strdata)

    def run(self):
        while True:
            try:
                if self.ws is None:
                    self.ws = websocket.WebSocketApp(self.url,
                                                on_message = self.on_message,
                                                on_error = self.on_error,
                                                on_close = self.on_close,
                                                on_open= self.on_open)
                    self.ws.run_forever()
            except Exception as e:
                self.logger.exception("hb websocket exception")

            self.logger.info("websocket may be closed and set self.ws to None")
            self.ws = None
            self.init_container()
            current_time = time.time()
            if current_time - self.last_open_time > 180:
                self.reconect_counts = 0
            else:
                # 过去180秒重连超过10次
                if self.reconect_counts > 10:
                    self.logger.info("warning:过去180秒重连超过10次")
            self.reconect_counts += 1
            self.logger.critical("reconnect counts: {}".format(self.reconect_counts))
            time.sleep(0.5)

            
if __name__ == "__main__":
    channels = ["market.BTC_CQ.kline.1min"]
    url = "wss://api.hbdm.com/ws_index"
    ws = HuobiDMWs(channels=channels,url=url)
    ws.start()
    i = 0
    while True:
        print("depth",ws.basis)
        time.sleep(1)
    



import websocket
import zlib
import json
import threading
import time,datetime
import logging
import hmac,base64

class OkexWs(threading.Thread):
    def __init__(self,channels=[],url=None,private_channels=None,ak=None):
        super().__init__()
        if url is None:
            self.url = "wss://real.OKEx.com:8443/ws/v3"
        else:
            self.url = url

        self.ws = None
        self.name = "okexWs"
        self.logger = logging.getLogger()
        self.init_container()

        self.private_channels = [] if private_channels is None else private_channels
        self.channels = [] if channels is None else channels
        self.ak = ak


    def init_container(self):
        self.ticker = dict()
        self.trade = dict()
        self.depth = dict()
        self.kline = dict()
        self.index = dict()

        self.last_msg_time = 0
        self.logged = False

    def login_params(self):
        api_key, passphrase, secret_key = self.ak["ak"],self.ak["pwd"],self.ak["sk"]
        timestamp = str(time.time())
        message = timestamp + 'GET' + '/users/self/verify'
        mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        sign = base64.b64encode(d)

        login_param = {"op": "login", "args": [api_key, passphrase, timestamp, sign.decode("utf-8")]}
        login_str = json.dumps(login_param)
        return login_str

    def on_message(self, message):
        message = self.inflate(message)
        if message == b"pong":
            self.logger.info(message)
            self.last_msg_time = time.time()
            return 
        else:
            message = json.loads(message)
            
            if message.get("event") == "login":
                if message["success"]:
                    topic = {"op": "subscribe", "args":self.private_channels}
                    topic = json.dumps(topic)
                    self.ws.send(topic)
                else:
                    self.logger.info(message)

        if "table" in message:
            table = message["table"]
            data = message["data"][0]
            instrument = data.get("instrument_id","")
        else:
            self.logger.info(message)
            return 

        channel = f"{table}:{instrument}"
        if table == "index/ticker":
            self.index[channel] = data
            
        elif table.endswith("ticker"):
            self.ticker[channel] = (data["best_ask"],data["best_bid"])
            
        elif table.endswith("depth5"):
            self.depth[channel] = data

        elif table.endswith("trade"):
            self.trade[channel] = data
            
        else:
            self.logger.info(message)

    def on_error(self, error):
        error = self.inflate(error)
        self.logger.info(error)

    def on_close(self):
        self.ws = None
        self.logger.info("### {}closed ###".format(self.name))

    def on_open(self):
        self.logger.info("{} websocket on_open".format(self.name))
        if self.ak:
            login = self.login_params() 
            self.ws.send(login)

        if self.channels:
            topic = {"op": "subscribe", "args": self.channels}
            topic = json.dumps(topic)
            self.last_open_time = time.time()
            self.ws.send(topic)
        if self.private_channels:
            t = threading.Thread(target=self.ping)
            t.start()

    
    def ping(self):
        while True:
            if time.time() - self.last_msg_time > 20:
                self.ws.send("ping")
            time.sleep(1)

    def get_timestamp(self):
        now = datetime.datetime.utcnow()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    def inflate(self,data):
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return inflated

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
                self.logger.info("websocket exception:{}".format(e))
            self.ws = None
            self.init_container()
            time.sleep(0.5)

            
if __name__ == "__main__":

    channels = []
    channels2 = []
    channels3 = []
    # channels = ["futures/ticker:EOS-USD-{}".format(x) for x in ["190104"]]
    
    channels2 = ["futures/depth5:EOS-USD-{}".format(x) for x in ["200626"]]
    # channels3 = ["futures/ticker:ETH-USD-{}".format(x) for x in ['190329',"181228","190104"]
    ws = OkexWs()
    ts = ws.get_timestamp()
    # print(ts)


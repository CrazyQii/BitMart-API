import websocket
import threading
import time
import sys, os
import json
import ast

DEBUG_MODE_SWITCH = False

class BinanceWs(object):
    def __init__(self, urlbase):
        self.sub_url = urlbase
        self.out_msg = {}
        
    def on_message(self, ws, message):
        # replace true, false in the string with True, False. Required by ast library
        message = message.replace("true", "True")
        message = message.replace("false", "False")
        original_message = ast.literal_eval(message)
        message = original_message["data"]
        new_message = {}
        
        if "lastUpdateId" in message.keys() and "bids" in message.keys() and "asks" in message.keys():
            # depth
            buys, sells = [], []
            for order in message["bids"]:
                buys.append({"price": order[0], "count": "1", "amount": order[1], "total": float(order[0]) * float(order[1])})
            for order in message["asks"]:
                sells.append({"price": order[0], "count": "1", "amount": order[1], "total": float(order[0]) * float(order[1])})
            new_message = {"code": 0, "data": {"buys": buys, "sells": sells}}
        elif "e" in message.keys() and message["e"] == "24hrTicker":
            # price
            data = {"c": message["c"], "rate": None, "v": message["v"], 
                    "h": message["h"], "sign": None, "time": message["E"], "l": message["l"], 
                    "increase": None, "fluctuation": None, "o": message["o"]}
            new_message = {"code": 0, "data": data, "local": None, "subscribe": "price", "symbol": message["s"], "uuid": None}
        elif "e" in message.keys() and message["e"] == "trade":
            # trade
            data = {"trades": [{"isBuy": 1 if int(message["b"]) > int(message["a"]) else 0,
                                "sequence": None, "amount": float(message["q"]) * float(message["p"]), "price": message["p"], 
                                "count": message["q"], "time": message["T"]}]}
            new_message = {"symbol": message["s"], "code": 0, "data": data, "subscribe": "trade", "precision": None, "firstSubscribe": 1}
        elif "e" in message.keys() and message["e"] == "kline":
            # kline
            new_message = {"code": 0, "data": {
                                            "o": message["k"]["o"],
                                            "h": message["k"]["h"],
                                            "l": message["k"]["l"],
                                            "v": message["k"]["v"],
                                            "c": message["k"]["c"],
                                            "ot": message["k"]["t"],
                                            "ct": message["k"]["T"],
                                            "t": message["E"]
                                            }, 
                            "step": None, "subscribe": "kline", "symbol": message["s"], "uuid": None
                            }
        else:
            new_message = {"code": 999, "error": "Endpoint not supported"}
        
        self.out_msg[original_message["stream"]] = new_message

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            time.sleep(3 * 60)
            while True:
                # keep alive
                # ws.send("""{"subscribe": "pong"}""")
                time.sleep(15)
            ws.close()
            print("thread terminating...")
            
        threading.Thread(target=run).start()


    def start_ws(self):
        # remove the last / in the sub_url
        self.sub_url = self.sub_url[:-1]
        
        websocket.enableTrace(DEBUG_MODE_SWITCH)     # DEBUG
        ws = websocket.WebSocketApp(self.sub_url, 
                                    on_message = lambda ws,msg: self.on_message(ws, msg),
                                    on_error   = lambda ws,msg: self.on_error(ws, msg),
                                    on_close   = lambda ws:     self.on_close(ws),
                                    on_open    = lambda ws:     self.on_open(ws))
        try:
            threading.Thread(target=ws.run_forever).start()
        except KeyboardInterrupt:
            sys.exit()

    # price for one symbol
    def sub_price(self, symbol):
        sub_name = ''.join(symbol.split('_')).lower() + "@ticker"
        self.sub_url += (sub_name + "/")
        self.out_msg[sub_name] = None
        return sub_name
                    
    # ticker for all markets, output is not cleaned
    def sub_market(self):
        sub_name = "!bookTicker"
        self.sub_url += (sub_name + "/")
        self.out_msg[sub_name] = None
        return sub_name
                        
    # order book
    def sub_depth(self, symbol):
        sub_name = ''.join(symbol.split('_')).lower() + "@depth20@100ms"
        self.sub_url += (sub_name + "/")
        self.out_msg[sub_name] = None
        return sub_name
                    
    # detailed trade
    def sub_trade(self, symbol):
        sub_name = ''.join(symbol.split('_')).lower() + "@trade"
        self.sub_url += (sub_name + "/")
        self.out_msg[sub_name] = None
        return sub_name
        
    # 1 min kline
    def sub_kline(self, symbol):
        sub_name = ''.join(symbol.split('_')).lower() + "@kline_1m"
        self.sub_url += (sub_name + "/")
        self.out_msg[sub_name] = None
        return sub_name
        
    # no auth endpoints
    def sub_notify(self, account_key):
        pass

    def sub_orders(self, account_key, pairs):
        pass
        
if __name__ == "__main__":
    bws = BinanceWs("wss://stream.binance.com:9443/stream?streams=")
    ch1 = bws.sub_depth("BTC_USDT")
    # print(depth_ws)
    ch2 = bws.sub_price("BTC_USDT")
    ch3 = bws.sub_trade("BTC_USDT")
    ch4 = bws.sub_kline("BTC_USDT")
    bws.start_ws()
    print()
    while True:
        for i in range(1000):
            print(bws.out_msg[ch1])
            print(bws.out_msg[ch2])
            print(bws.out_msg[ch3])
            print(bws.out_msg[ch4])
            time.sleep(2)

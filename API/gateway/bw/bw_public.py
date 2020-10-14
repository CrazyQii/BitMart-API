from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import re
import os
import json
import requests
import time
from exchange_public import ExchangePublic


class BwPublic(ExchangePublic):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        url = self.urlbase + "api/data/v1/ticker?marketName=%s" % (symbol)
        is_ok, content = self.request("GET", url)

        if not is_ok:
            self.output("get_price", content)
        else:
            return float(content["datas"][1])

    def get_price_increment(self, symbol):
        try: 
            current_path = os.path.dirname(os.path.abspath(__file__))
            with open(current_path + "/bw_markets_details.json", "r") as f:
                market_details = json.load(f)
            f.close()
            for market in market_details:
                if symbol.lower() == market["name"]:
                    return 1.0 / 10 ** float(market["priceDecimal"])
            return 0.01
        except Exception as e:
            print(e)
        
    def get_price_precision(self, symbol):
        try: 
            current_path = os.path.dirname(os.path.abspath(__file__))
            with open(current_path + "/bw_markets_details.json", "r") as f:
                market_details = json.load(f)
            f.close()
            
            for market in market_details:
                if symbol.lower() == market["name"]:
                    return int(market["priceDecimal"])
            return 2
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        url = self.urlbase + "api/data/v1/entrusts?marketName=%s&dataSize=%s" % (symbol, 50)
        is_ok, content = self.request("GET", url)

        if not is_ok:
            self.output("get_orderbook", content)
        else:
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in content["datas"]["bids"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in content["datas"]["asks"][::-1]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook

    def get_kline(self, symbol, timeperiod=360, interval=1):
        url = self.urlbase + "api/data/v1/klines?marketName=%s&type=1M&dataSize=100" % (symbol)
        is_ok, content = self.request("GET", url)
        
        if not is_ok:
            self.output("get_kline", content)
        else:
            results = []
            for k in content["datas"]:
                results.append({"timestamp": int(k[3]) * 1000, 
                                "volume": k[8], 
                                "open_price": k[4], 
                                "current_price": k[7], 
                                "lowest_price": k[6], 
                                "highest_price": k[5]})
            return results

    def get_trades(self, symbol):
        url = self.urlbase + "api/data/v1/trades?marketName=%s&dataSize=20" % (symbol)
        is_ok, content = self.request("GET", url)
        
        if not is_ok:
            self.output("get_trades", content)
        else:
            results = []
            for trade in content["datas"]:
                results.append({"amount": float(trade[5]) * float(trade[6]), 
                                "count": float(trade[6]), 
                                "type": "buy" if trade[4] == "bid" else "sell", 
                                "price": float(trade[5]), 
                                "order_time": int(trade[2]) * 1000})
            return results
            
    def get_ticker(self, symbol):
        url = self.urlbase + "api/data/v1/ticker?marketName=%s" % (symbol)
        is_ok, content = self.request("GET", url)
        
        if not is_ok:
            self.output("get_ticker", content)
        else:
            data = content["datas"]
            return {"bid_1_amount": None, 
                    "symbol_id": symbol, 
                    "url": url, 
                    "fluctuation": data[5], 
                    "base_volume": data[9], 
                    "ask_1_amount": None, 
                    "volume": data[4], 
                    "current_price": data[1], 
                    "bid_1": data[7], 
                    "lowest_price": data[3], 
                    "ask_1": data[8], 
                    "highest_price": data[2]}
    
    def dump_json(self, data, file_name):
        try:
            is_file = os.path.isfile(file_name)
            path = os.path.join(os.path.split(os.path.realpath(__file__))[0], file_name)
            with open(path, "w+") as f:
                data_json = json.dumps(data, indent = 4)
                f.write(data_json)
            f.close()
        except Exception as e:
            print(e)

    def get_markets(self):
        url = self.urlbase + "exchange/config/controller/website/marketcontroller/getByWebId"
        is_ok, content = self.request("POST", url)
        
        if not is_ok:
            self.output("get_markets", content)
        else:
            self.dump_json(content["datas"], "bw_markets_details.json")

    def get_currencies(self):
        url = self.urlbase + "exchange/config/controller/website/currencycontroller/getCurrencyList"
        is_ok, content = self.request("POST", url)
        
        if not is_ok:
            self.output("get_currencies", content)
        else:
            self.dump_json(content["datas"], "bw_currencies_details.json")


if __name__ == "__main__":
    goko_public = BwPublic("https://www.BW.com/")
    # print(goko_public.get_price_increment("EOS_USDT"))
    # print(goko_public.get_price_precision("EOS_USDT"))
    # print(goko_public.get_price("SDC_ETH"))
    # print(goko_public.get_trades("SDC_ETH"))
    print(goko_public.get_orderbook("SDC_ETH")["sells"])
    # print(goko_public.get_kline("BTC_USDT"))
    # print(goko_public.get_ticker("BTC_USDT"))
    # print(goko_public.get_markets())
    # print(goko_public.get_currencies())


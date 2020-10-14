import requests
import time
import os
import json

class GateioPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        try:
            url = self.urlbase + "spot/tickers?currency_pair=%s" % (symbol)
            response = requests.get(url)
            return float(response.json()[0]["last"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "spot/order_book?currency_pair=%s&limit=20" % symbol
            response = requests.get(url)
            data = response.json()
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["asks"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

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

    def get_symbols_details(self):
        try:
            url = self.urlbase + "spot/currency_pairs"
            response = requests.get(url).json()
            self.dump_json(response, "gateio_markets_details.json")
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/gateio_markets_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print (e)

    def get_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            for pair in symbols_details:
                if pair["id"] == symbol:
                    return int(pair["precision"])
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            return float(1.0 / 10 ** self.get_precision(symbol))
        except Exception as e:
            print (e)
    
    def get_trades(self, symbol):
        try:
            url = self.urlbase + "spot/trades?currency_pair=%s&limit=40" % symbol
            response = requests.get(url)
            results = []
            for trade in response.json():
                results.append({
                    "count": trade["amount"], 
                    "amount": float(trade["amount"]) * float(trade["price"]), 
                    "price": trade["price"], 
                    "type": trade["side"], 
                    "order_time": trade["create_time"]
                })
            return results
        except Exception as e:
            print (e)

if __name__ == "__main__":
    gate_public = GateioPublic("https://api.gateio.ws/api/v4/")
    # print(gate_public.get_price("GRIN_USDT"))
    # print(gate_public.get_orderbook("GRIN_USDT"))
    # print(gate_public.get_symbols_details())
    # print(gate_public.load_symbols_details())
    # print(gate_public.get_precision("GRIN_USDT"))
    # print(gate_public.get_quote_increment("GRIN_USDT"))
    # print(gate_public.get_trades("GRIN_USDT"))

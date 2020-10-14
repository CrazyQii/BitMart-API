import requests
import os
import json
import math


class yobitPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/yobit_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def symbol_convert(self, symbol):
        pass

    def get_price(self, symbol):
        try:
            ticker = self.get_ticker(symbol)
            return ticker["current_price"]
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = "https://yobit.net/api/3/depth/%s" % symbol.lower()
            response = requests.get(url)
            data = response.json()[symbol.lower()]
            buys, sells = [], []
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                buys.append(tmp)
            for i in data["asks"]:#[::-1]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                sells.append(tmp)
            return {"buys": buys, "sells": sells}
        except Exception as e:
            print(e)
            return {"buys":[], "sells":[]}

    def get_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(symbols_details[symbol]["price_max_precision"])
        except Exception as e:
            print(e)

    def get_quote_increment(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return float(symbols_details[symbol]["quote_increment"])
        except Exception as e:
            print(e)

    def get_amount_precision(self, symbol):
        try:
            symbols_details = self.load_symbols_details()
            return int(abs(math.log10(float(symbols_details[symbol]["base_min_size"]))))
        except Exception as e:
            print(e)

    def get_ticker(self, symbol):
        url = "https://yobit.net/api/3/ticker/%s" % symbol.lower()
        content = requests.request("GET", url)
        content = content.json()[symbol.lower()]
        dict = {}
        dict['volume'] = content["vol"]
        dict['ask_1'] = content["sell"]
        dict['lowest_price'] = content["low"]
        dict['bid_1'] = content["buy"]
        dict['highest_price'] = content["high"]
        dict['base_volume'] = content["vol_cur"]
        dict['current_price'] = content["last"]
        dict['fluctuation'] = None
        dict['symbol_id'] = symbol
        return dict

    def get_trades(self, symbol):
        try:
            url = "https://yobit.net/api/3/trades/%s" % symbol.lower()
            response = requests.get(url)
            results = []
            for trade in response.json()[symbol.lower()]:
                results.append({
                    "count": trade["amount"],
                    "amount": float(trade["amount"]) * float(trade["price"]),
                    "price": trade["price"],
                    "type": "sell" if trade["type"] == "ask" else "buy",
                    "order_time": trade["timestamp"]
                })
            return results
        except Exception as e:
            print(e)


if __name__ == "__main__":
    ybt_public = yobitPublic("")
    # print(ybt_public.get_price("HEX_BTC"))
    # print(ybt_public.get_ticker("HEX_BTC"))
    # print(ybt_public.get_orderbook("HEX_BTC"))
    # print(ybt_public.get_precision("HEX_BTC"))
    # print(ybt_public.get_quote_increment("HEX_BTC"))
    # print(ybt_public.get_trades("HEX_BTC"))


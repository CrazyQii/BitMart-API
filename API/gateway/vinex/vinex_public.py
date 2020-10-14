import re
import requests
import time
import os
import json
import math


class VinexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/vinex_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def symbol_convert(self, symbol):
        symbol_pair = re.findall("[A-Z]+", symbol)
        symbol_base = symbol_pair[0]
        symbol_quote = symbol_pair[1]
        coin = symbol_quote + "_" + symbol_base
        return coin

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "markets/%s" % symbol
            response = requests.get(url)
            return response.json()["data"]["lastPrice"]
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "get-order-book?market=%s" % symbol
            response = requests.get(url)
            data = response.json()["data"]
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = i["price"]
                tmp["amount"] = i["quantity"]
                total_amount_buys += i["quantity"]
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in data["asks"]:#[::-1]:
                tmp = {}
                tmp["price"] = i["price"]
                tmp["amount"] = i["quantity"]
                total_amount_sells += i["quantity"]
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

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
            return int(abs((symbols_details[symbol]["base_min_size"])))
        except Exception as e:
            print(e)

    def get_ticker(self, symbol):
        symbol = self.symbol_convert(symbol)
        url = self.urlbase + "get-ticker?market=%s" % symbol
        content = requests.request("GET", url)
        content = content.json()['data']
        dict = {}
        dict['volume'] = content['volume']
        dict['ask_1'] = content['askPrice']
        dict['lowest_price'] = content['lowPrice']
        dict['bid_1'] = content['bidPrice']
        dict['highest_price'] = content['highPrice']
        dict['base_volume'] = content['baseVolume']
        dict['current_price'] = content['lastPrice']
        dict['fluctuation'] = content['change24h']
        dict['symbol_id'] = content['symbol'].upper()
        return dict

    def get_trades(self, symbol , limit = 100):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "get-market-history?market=%s" % symbol
            response = requests.get(url)
            results = []
            for trade in response.json()["data"]:
                results.append({
                    "count": trade["amount"],
                    "amount": float(trade["amount"]) * float(trade["price"]),
                    "price": trade["price"],
                    "type": "sell" if trade["type"] == 0 else "buy",
                    "order_time": trade["createdAt"]
                })
            return results
        except Exception as e:
            print(e)


if __name__ == "__main__":
    v_public = VinexPublic("https://api.vinex.network/api/v2/")
    # print(v_public.get_price("VEIL_BTC"))
    # print(v_public.get_ticker("BTC_ETH"))
    # print(v_public.get_orderbook("VEIL_BTC"))
    # print(v_public.get_precision("BTC_ETH"))
    # print(v_public.get_quote_increment("BTC_ETH"))
    # print(v_public.get_trades("BTC_ETH"))


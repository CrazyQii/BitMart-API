import re
import requests
import time
import os
import json


class DigiFinexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        try:
            url = self.urlbase + "ticker?symbol=%s" % symbol.lower()
            response = requests.get(url)
            return float(response.json()["ticker"][0]["last"])

        except Exception as e:
            print(e)
            return None

    # limit default 10, max 150
    def get_orderbook(self, symbol, limit = 10):
        try:
            url = self.urlbase + "order_book?symbol=%s&limit=%s" % (symbol.lower(), limit)
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
            for i in data["asks"][::-1]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            return orderbook
        except Exception as e:
            print(e)

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/digifinex_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
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

    def get_ticker(self, symbol):
        url = self.urlbase + "ticker?symbol=%s" % symbol.lower()
        content = requests.request("GET", url)
        # if not is_ok:
        #     self.output("get_ticker", content)
        # else:
        content = content.json()['ticker'][0]
        dict = {}
        dict['volume'] = content['vol']
        dict['ask_1'] = content['sell']
        dict['lowest_price'] = content['low']
        dict['bid_1'] = content['buy']
        dict['highest_price'] = content['high']
        dict['base_volume'] = content['base_vol']
        dict['current_price'] = content['last']
        dict['fluctuation'] = content['change']
        dict['symbol_id'] = content['symbol'].upper()

        return dict

    # limit default 100, max 500
    def get_trades(self, symbol , limit = 100):
        try:
            url = self.urlbase + "trades?symbol=%s&limit=%s" % (symbol.lower(), limit)
            response = requests.get(url)
            results = []
            for trade in response.json()["data"]:
                results.append({
                    "count": trade["amount"],
                    "amount": float(trade["amount"]) * float(trade["price"]),
                    "price": trade["price"],
                    "type": trade["type"].lower(),
                    "order_time": trade["date"] * 1000
                })
            return results
        except Exception as e:
            print(e)


if __name__ == "__main__":
    d_public = DigiFinexPublic("https://openapi.digifinex.vip/v3/")
    # print(idax_public.get_price("APL_ETH"))
    print(d_public.get_orderbook("APL_ETH"))
    # print(idax_public.load_symbols_details())
    # print(idax_public.get_precision("APL_ETH"))
    # print(idax_public.get_quote_increment("APL_ETH"))
    # print(idax_public.get_trades("APL_ETH"))
    # print(d_public.get_price('BTC_USDT'))
# 
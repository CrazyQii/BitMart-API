import requests
import re
import json
import os
import time


class CmcAuth(object):
    def __init__(self, urlbase, token):
        self.cmc_ids = {}
        self.urlbase = urlbase
        # self.token = token
        self.headers = {
            "X-CMC_PRO_API_KEY": token
        }

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "/" + symbol_quote
        except Exception as e:
            print(e)

    def symbol_convert_to_bitmart(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_base + "_" + symbol_quote
        except Exception as e:
            print (e)

    def get_exchanges(self):
        try:
            url = self.urlbase + "v1/exchange/listings/latest"
            response = requests.get(url, headers=self.headers)
            print (response.content)
            return response.json()
        except Exception as e:
            print (e)

    def get_exchange_ranking(self, exchange):
        try:
            url = self.urlbase + "v1/exchange/listings/latest?sort=volume_24h_adjusted"
            response = requests.get(url, headers=self.headers)
            current_ranking = 1
            for i in response.json()["data"]:
                if i["slug"] == exchange:
                    return current_ranking, i["quote"]["USD"]["volume_24h"]
                else:
                    current_ranking += 1
            return 0
        except Exception as e:
            print (e)

    def get_all_exchange_ranking(self):
        try:
            url = self.urlbase + "v1/exchange/listings/latest?sort=volume_24h_adjusted"
            response = requests.get(url, headers=self.headers)
            results = []
            for i in response.json()["data"]:
                results.append((i["slug"], i["quote"]["USD"]["volume_24h"]))
            return results
        except Exception as e:
            print(e)

    def get_exchange_liquidity_ranking(self, exchange):
        try:
            # liquidity ranking info is not yet available in its api
            url = "https://web-api.coinmarketcap.com/v1/exchange/listings/latest?aux=num_market_pairs,date_launched&convert=USD&limit=400&sort=volume_24h_adjusted&sort_dir=desc&start=1"
            response = requests.get(url, headers=self.headers)
            current_ranking = 1
            liquidity_list = []
            for i in response.json()["data"]:
                if i["quote"]["USD"]["effective_liquidity_24h"] is not None:
                    liquidity_list.append((i["slug"], i["quote"]["USD"]["effective_liquidity_24h"]))

            liquidity_list.sort(key=lambda x: x[1], reverse=True)
            for (slug, liquidity) in liquidity_list:
                if exchange == slug:
                    return current_ranking, liquidity
                else:
                    current_ranking += 1
            return 0
        except Exception as e:
            print(e)

    def get_exchange_symbols_daily_volume(self, exchange):
        try:
            url = self.urlbase + "v1/exchange/market-pairs/latest?limit=5000&slug=%s" % exchange
            response = requests.get(url, headers=self.headers)
            symbols_daily_volume = {}
            for i in response.json()["data"]["market_pairs"]:
                symbol = self.symbol_convert_to_bitmart(i["market_pair"])
                volume_detail = {}
                volume_detail["price"] = i["quote"]["USD"]["price"]
                volume_detail["daily_volume"] = i["quote"]["USD"]["volume_24h"]
                symbols_daily_volume[symbol] = volume_detail
            return symbols_daily_volume
        except Exception as e:
            print (e)

    def get_symbol_daily_volume(self, exchange, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/exchange/market-pairs/latest?limit=5000&slug=%s" % exchange
            response = requests.get(url, headers=self.headers)
            for i in response.json()["data"]["market_pairs"]:
                if symbol == i["market_pair"]:
                    volume_detail = {}
                    volume_detail["price"] = i["quote"]["USD"]["price"]
                    volume_detail["daily_volume"] = i["quote"]["USD"]["volume_24h"]
                    return volume_detail
            return None
        except Exception as e:
            print (e)

if __name__ == "__main__":
    cmc_auth = CmcAuth("https://pro-api.coinmarketcap.com/", "af184f11-da03-4826-a427-eab1cedfca78")
    # print cmc_auth.get_exchange_symbols_daily_volume("binance")
    # print cmc_auth.get_symbol_daily_volume("binance", "BTC_USDT")
    # print (cmc_auth.get_exchange_ranking("bitmart"))
    # print(cmc_auth.get_exchange_ranking("binance"))
    # print(cmc_auth.get_exchange_liquidity_ranking("bitmart"))
    # print(cmc_auth.get_all_exchange_ranking())
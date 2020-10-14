import requests
import json
import time
import configparser

class DdexPublic(object):
    def getMarketInfo(self, symbol):
        try:
            url = "https://api.ddex.io/v2/markets/%s" % symbol
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(e)

    def getMaxPrecision(self, symbol):
        try:
            url = "https://api.ddex.io/v2/markets/%s" % symbol
            response = requests.get(url)
            pricePrecision = response.json()["data"]["market"]["priceDecimals"]
            return pricePrecision
        except Exception as e:
            print(e)

    def getTicker(self, symbol):
        try:
            url = "https://api.ddex.io/v2/markets/%s/ticker" % symbol
            response = requests.get(url)
            return response.json()["data"]["ticker"]
        except Exception as e:
            print(e)

    def getOrderBook(self, symbol):
        try:
            url = "https://api.ddex.io/v2/markets/%s/orderbook" % symbol
            response = requests.get(url)
            return response.json()["data"]["orderBook"]
        except Exception as e:
            print(e)


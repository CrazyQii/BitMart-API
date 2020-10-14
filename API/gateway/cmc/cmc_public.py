import requests
import re
import json
import os


class CmcPublic(object):
    def __init__(self, urlbase):
        self.cmc_ids = {}
        self.urlbase = urlbase
        try:
            current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(current_path + "/cmc/cmc_id.json", "r") as f:
                cmc_response = json.load(f)
            f.close()

            symbols = cmc_response['data']

            for symbol in symbols:
                self.cmc_ids[symbol['symbol']] = int(symbol['id'])

        except Exception as e:
            print(e)


    def get_price(self, symbol):
        try:
            symbolPair = re.findall("[A-Z]+", symbol)
            symbolBase = symbolPair[0]
            symbolQuote = symbolPair[1]
            cmc_id = self.cmc_ids[symbolBase]

            url = self.urlbase + "v2/ticker/%s/?convert=%s" % (cmc_id, symbolQuote)
            response = requests.get(url)
            return float(response.json()["data"]["quotes"][symbolQuote]["price"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    cmc_public = CmcPublic("https://api.coinmarketcap.com/")
    print (cmc_public.get_price("BTC_USDT"))

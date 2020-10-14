import re
import requests
import time

class BitzPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            return symbol.lower()
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/ticker?symbol=%s" % (symbol)
            response = requests.get(url)
            # print(response.content)
            return float(response.json()["data"]["now"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    bitz_public = BitzPublic("https://apiv2.bitz.com/")
    print (bitz_public.get_price("QTUM_BTC"))
    # for i in range(1, 20):
    #     print bitz_public.get_adjusted_trade("BTC_USDT")
    #     time.sleep(5)

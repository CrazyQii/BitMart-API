import re
import requests
import time

class BitforexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return "coin" + "-" + symbol_quote.lower() + "-" + symbol_base.lower()
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/ticker?symbol=%s" % (symbol)
            response = requests.get(url)
            # print(response.content)
            return float(response.json()["data"]["last"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    bitforex_public = BitforexPublic("https://api.bitforex.com/api/v1/")
    print (bitforex_public.get_price("HYDRO_ETH"))
    # for i in range(1, 20):
    #     print bitforex_public.get_adjusted_trade("BTC_USDT")
    #     time.sleep(5)

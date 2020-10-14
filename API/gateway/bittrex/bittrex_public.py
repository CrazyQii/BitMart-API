import re
import requests
import time

class BittrexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return symbol_quote + "-" + symbol_base
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "public/getticker?market=%s" % (symbol)
            response = requests.get(url)
            # print(response.content)
            return float(response.json()["result"]["Last"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    bittrex_public = BittrexPublic("https://bittrex.com/api/v1.1/")
    print (bittrex_public.get_price("HYDRO_BTC"))
    # for i in range(1, 20):
    #     print bittrex_public.get_adjusted_trade("BTC_USDT")
    #     time.sleep(5)

import re
import requests

class HitbtcPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def symbol_convert(self, symbol):
        try:
            if symbol == "ZEC_USDT":
                return "ZECUSD"
            elif symbol == "EOS_USDT":
                return "EOSUSD"
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            if symbol_base == "BSV":
                symbol_base = "BCHSV"
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "public/ticker/%s" % (symbol)
            response = requests.get(url)
            # print response.content
            return float(response.json()["last"])

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    Hitbtc_public = HitbtcPublic("https://api.hitbtc.com/api/2/")
    # print Hitbtc_public.get_price("ZEC_USDT")

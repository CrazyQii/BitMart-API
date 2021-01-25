import re
import requests
import time
import os
import json
from Gateway.kucoin.kucoin_public import KucoinPublic

class RefKucoinPublic(object):
    def __init__(self, urlbase):
        self.kucoin_public = KucoinPublic(urlbase)

    def symbol_convert(self, symbol):
        try:
            if symbol == "ODE_BTC":
                return ("ODE_USDT", "BTC_USDT", 1)
            if symbol == "ODE_ETH":
                return ("ODE_USDT", "ETH_USDT", 1)
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            if symbol_quote == "BTC" or symbol_quote == "USDT":
                return (symbol_base + "_ETH", "ETH_" + symbol_quote, 0)
            elif symbol_quote == "ETH":
                return (symbol_base + "_BTC", "ETH_BTC", 1)
            elif symbol_quote == "BMX":
                return (symbol_base + "_ETH", "BMX_ETH", 1)
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            base_pair, quote_pair, operator = self.symbol_convert(symbol)
            price_base = float(self.kucoin_public.get_price(base_pair))
            price_quote = float(self.kucoin_public.get_price(quote_pair))
            if operator == 0:
                return price_base * price_quote
            elif operator == 1:
                if price_quote == 0:
                    return 0
                else:
                    return price_base / price_quote

        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    ref_kucoin_public = RefKucoinPublic("https://api.kucoin.com/")
    # print ref_kucoin_public.get_price("ODE_BTC")

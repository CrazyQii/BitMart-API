import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from restful import UbiexSDK

class XtPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase
        self.xtsdk = UbiexSDK("", "")

    def load_symbols_details(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            symbols_details = {}
            with open(current_path + "/xt_symbols_details.json", "r") as f:
                symbols_details = json.load(f)
            f.close()
            return symbols_details
        except Exception as e:
            print(e)

    def symbol_convert(self, symbol):
        try:
            symbol = symbol.lower()
            return symbol
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            ticker = self.xtsdk.getTicker(symbol)
            return ticker["price"]
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            depth = self.xtsdk.getDepth(symbol)

            buys, sells = [], []
            total_amount_buys = 0
            total_amount_sells = 0
            for i in depth["bids"]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                buys.append(tmp)
            for i in depth["asks"]:#[::-1]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                sells.append(tmp)
            return {"buys": buys, "sells": sells}
           
        except Exception as e:
            print(e)
            return {"buys":[], "sells":[]}

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
        try:
            symbol = self.symbol_convert(symbol)
            ticker = self.xtsdk.getTicker(symbol)
            return ticker
        except Exception as e:
            print(e)

    def get_trades(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            trades = self.xtsdk.getTrades(symbol)
            results = []
            for trade in trades:
                results.append({
                    "amount": float(trade[2]),
                    "price": trade[1],
                    "type": "sell" if trade[3] == "ask" else "buy",
                    "order_time": trade[0]
                })
            return results
        except Exception as e:
            print(e)


if __name__ == "__main__":
    xt_public = XtPublic("")
    # print(xt_public.get_price("BTC_USDT"))
    # print(xt_public.get_ticker("BTC_USDT"))
    # print(xt_public.get_orderbook("BTC_USDT"))
    # print(xt_public.get_precision("HEX_USDT"))
    # print(xt_public.get_quote_increment("HEX_USDT"))
    print(xt_public.get_trades("BTC_USDT"))


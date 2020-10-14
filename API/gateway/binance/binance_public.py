import re
import requests
import time
from urllib.parse import urlencode

class BinancePublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase
        self.session = requests.session()

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            if symbol_base == "GXC":
                symbol_base = "GXS"
            if symbol_base == "BSV":
                symbol_base = "BCHSV"
            # if symbol_base == "BCH":
            #     symbol_base = "BCHABC"
            return symbol_base + symbol_quote
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v3/ticker/price?symbol=%s" % (symbol)
            response = requests.get(url)
            # print(response.content)
            price = float(response.json()["price"])
            if price is None:
                print(response.content)
            return price

        except Exception as e:
            print(e)
            return None

    def get_bid1_ask1(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/ticker/24hr?symbol=%s" % (symbol)
            response_json = requests.get(url).json()
            bid1 = float(response_json["bidPrice"])
            ask1 = float(response_json["askPrice"])
            return (bid1, ask1)
        except Exception as e:
            print(e)
            return (None, None)


    def get_adjusted_trade(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/trades?symbol=%s&limit=100" % (symbol)
            response = requests.get(url)
            price = float(response.json()[0]["price"])
            quantity = float(response.json()[0]["qty"])
            for i in response.json():

                if float(i["qty"]) > quantity:
                    price = float(i["price"])
                    quantity = float(i["qty"])
            return (price, quantity)
        except Exception as e:
            print(e)

    def get_last_trade(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/trades?symbol=%s&limit=1" % (symbol)
            response = requests.get(url)
            # print(response.content)
            return (float(response.json()[0]["price"]), float(response.json()[0]["qty"]))
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol,n=100):
        try:
            symbol = self.symbol_convert(symbol)
            params = {
                "symbol":symbol,
                "limit":n
            }
            url = self.urlbase + "v3/depth?" + urlencode(params)
            response = self.session.get(url)
            orderbook = {"buys": [], "sells": []}
            total_amount_buys = 0
            total_amount_sells = 0
            for i in response.json()["bids"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                orderbook["buys"].append(tmp)
            for i in response.json()["asks"]:
                tmp = {}
                tmp["price"] = float(i[0])
                tmp["amount"] = float(i[1])
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                orderbook["sells"].append(tmp)
            # full size of the orderbook is 100
            return orderbook
        except Exception as e:
            print(e)
            return None

    def get_precision(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/exchangeInfo"
            response = self.session.get(url)
            symbols = response.json()["symbols"]
            for i in symbols:
                if i["symbol"] == symbol:
                    return int(i["baseAssetPrecision"])
        except Exception as e:
            print (e)
            
    def get_exchangeinfo(self):
        url = self.urlbase + "v1/exchangeInfo"
        response = self.session.get(url)  
        return response.json()      

    def get_kline(self, symbol, timeperiod=12000, interval=1):
        try:
            current_timestamp = int(time.time())
            from_timestamp = current_timestamp - timeperiod
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "v1/klines?symbol=%s&interval=1m&startTime=%s&endTime=%s" % (symbol, str((from_timestamp * 1000)), str((current_timestamp * 1000)))
            response = self.session.get(url)

            results = []
            for row in response.json():
                results.append({
                    "timestamp": int(row[0]/1000),
                    "open": row[1],
                    "high": row[2],
                    "low": row[3],
                    "close": row[4],
                    "volume": row[5],
                    "last_price": row[4]
                    })
            return results
        except Exception as e:
            print (e)

    def get_exchange_status(self):
        try:
            url_trade = self.urlbase + "v1/trades?symbol=BTCUSDT&limit=100"
            response_trade = requests.get(url_trade)
            if response_trade.status_code != 200:
                return False
            current_timestamp = int(time.time())
            last_trade_timestamp = int(response_trade.json()[0]["time"]) / 1000
            if (current_timestamp - last_trade_timestamp) > 1 * 60:
                return False
            return True
        except Exception as e:
            print(e)


if __name__ == "__main__":
    binance_public = BinancePublic("https://api.binance.com/api/")
    # print(binance_public.get_bid1_ask1("BTC_USDT"))
    # print(binance_public.get_price("BTC_USDT"))
    # print(binance_public.get_adjusted_trade("BTC_USDT"))
    # print(binance_public.get_last_trade("BTC_USDT"))
    # print(binance_public.get_orderbook("BTC_USDT"))
    print(binance_public.get_kline("BTC_USDT"))
    # print(binance_public.get_exchange_status())
    # for i in range(1, 20):
    #     print(binance_public.get_adjusted_trade("BTC_USDT"))
    #     time.sleep(5)

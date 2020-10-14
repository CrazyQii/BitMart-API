import re
import requests
import time

class HuobiPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase
        self.request_header = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
        }

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return (symbol_base + symbol_quote).lower()
        except Exception as e:
            print(e)

    def get_price(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/trade?symbol=%s" % (symbol)
            response = requests.get(url, headers=self.request_header)
            data = response.json()["tick"]["data"]
            return float(data[0]["price"])

        except Exception as e:
            print(e)
            return None

    def get_kline(self, symbol, timeperiod=200, interval="1min"):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "/market/history/kline?period=%s&size=%s&symbol=%s" % (interval, timeperiod, symbol)
            response = requests.get(url, headers=self.request_header)
            data = response.json()["data"]
            results = []
            for row in data:
                results.append({
                    "timestamp": row["id"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["amount"],
                    "last_price": row["close"]
                    })
            return results
        except Exception as e:
            print("Huobi Public: get kline error: %s" % e)

    def get_last_trade(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/trade?symbol=%s" % (symbol)
            response = requests.get(url, headers=self.request_header)
            data = response.json()["tick"]["data"]
            return (float(data[0]["price"]), float(data[0]["amount"]))
        except Exception as e:
            print(e)

    def get_orderbook(self, symbol):
        try:
            symbol = self.symbol_convert(symbol)
            url = self.urlbase + "market/depth?symbol=%s&type=step0" % (symbol)
            response = requests.get(url, headers=self.request_header)
            # print(response.content)
            return response.json()
        except Exception as e:
            print (e)

    def get_exchange_status(self):
        try:
            url_trade = self.urlbase + "market/trade?symbol=htusdt"
            response_trade = requests.get(url_trade)
            if response_trade.status_code != 200:
                return False
            current_timestamp = int(time.time())
            last_trade_timestamp = int(response_trade.json()["tick"]["ts"]) / 1000
            if (current_timestamp - last_trade_timestamp) > 10 * 60:
                return False
            return True
        except Exception as e:
            print(e)

if __name__ == "__main__":
    huobi_public = HuobiPublic("https://api.huobi.pro/")
    # print huobi_public.get_orderbook("BTC_USDT")
    print(huobi_public.get_kline("BTC_USDT"))

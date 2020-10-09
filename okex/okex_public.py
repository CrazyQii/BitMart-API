import requests
import datetime
import traceback
import time

class OkexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def request(self, method, path, data=None, headers=None):
        try:
            resp = requests.request(method, path, data=data, headers=headers)

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    "url": path,
                    "method": method,
                    "data": data,
                    "code": resp.status_code,
                    "msg": resp.text
                }
                return False, error
        except Exception as e:
            error = {
                "url": path,
                "method": method,
                "data": data,
                "traceback": traceback.format_exc(),
                "error": e
            }
            return False, error

    def output(self, function_name, content):
        info = {
            "func_name": function_name,
            "content": content
        }
        print(info)

    def get_price(self, symbol):
        try:
            url = self.urlbase + "api/spot/v3/instruments/%s/ticker" % ('-'.join(symbol.split("_")))
            response = requests.get(url)
            return float(response.json()["last"])

        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = self.urlbase + "api/spot/v3/instruments/%s/book" % ('-'.join(symbol.split("_")))
            response = requests.get(url).json()
            # This step leaves out the order counts from OKEX API response
            orderbook = {"asks": [[float(i[0]), float(i[1])] for i in response["asks"]], "bids": [[float(i[0]), float(i[1])] for i in response["bids"]]}
            return orderbook
        except Exception as e:
            print(e)

    def get_utility(self, accessType):
        pass

    def load_symbols_details(self):
        pass

    def get_precision(self, symbol):
        pass

    def get_quote_increment(self, symbol):
        pass

    def get_ticker(self, symbol):
        url = self.urlbase + "api/spot/v3/instruments/%s/ticker" % ('-'.join(symbol.split("_")))
        is_ok, okex_content = self.request("GET", url)

        if not is_ok:
            self.output("get_ticker", okex_content)
        else:
            content = {
                "bid_1_amount": None,
                "symbol_id": symbol,
                "url": url,
                "fluctuation": None,
                "base_volume": okex_content["base_volume_24h"],
                "ask_1_amount": None,
                "volume": okex_content["quote_volume_24h"],
                "current_price": okex_content["last"],
                "bid_1": okex_content["bid"],
                "lowest_price": okex_content["low_24h"],
                "ask_1": okex_content["ask"],
                "highest_price": okex_content["high_24h"]
            }
            return content

    def get_trades(self, symbol):
        url = self.urlbase + "api/spot/v3/instruments/%s/trades" % ('-'.join(symbol.split("_")))
        is_ok, okex_content = self.request("GET", url)
        content = []
        for trade in okex_content:
            content.append({
                "count": trade["size"],
                "amount": float(trade["size"]) * float(trade["price"]),
                "type": trade["side"],
                "price": trade["price"],
                "order_time": trade["timestamp"]
            })

        if not is_ok:
            self.output("get_trades", content)
            return {"price": "0.0", "amount": "0.0"}
        else:
            return content

    '''
    This part may need further work 
    I didn't find the minimum order size for OKEX
    '''
    def is_valid_price(self, symbol, price, amount):
        if "_ETH" in symbol and amount * price > 0.02:
            return True
        elif "_BTC" in symbol and amount * price > 0.0015:
            return True
        elif "_USDT" in symbol and amount * price > 5.0:
            return True
        return False

    def get_kline(self, symbol, time_period = 360):
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(seconds = time_period)
        url = self.urlbase + "api/spot/v3/instruments/%s/candles?granularity=60&start=%sZ&end=%sZ" % ('-'.join(symbol.split("_")), start.isoformat(), end.isoformat())
        is_ok, okex_content = self.request("GET", url)
        content = []
        for line in okex_content:
            content.append({
                "timestamp": line[0],
                "volume": line[5],
                "open_price": line[1],
                "current_price": line[4],
                "lowest_price": line[3],
                "highest_price": line[2]
            })

        if not is_ok:
            self.output("get_kline", content)
        else:
            return content

    def get_exchange_status(self):
        try:
            url_trade = self.urlbase + "api/spot/v3/instruments/OKB-USDT/ticker"
            response_trade = requests.get(url_trade)
            if response_trade.status_code != 200:
                return False
            current_timestamp = int(time.time())
            last_trade_timestamp = int(time.mktime(time.strptime(response_trade.json()["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")))
            if (current_timestamp - last_trade_timestamp) > 5 * 60:
                return False
            return True
        except Exception as e:
            print(e)


if __name__ == "__main__":
    okex = OkexPublic("https://www.okex.com/")
    # print (okex.get_exchange_status())
    # print(okex.get_orderbook("BTC_USDT"))
    print(okex.get_price("LTC_BTC"))
    # print(okex.get_ticker("LTC_BTC"))
    # print(okex.get_trades("LTC_BTC"))
    # print(okex.get_kline("LTC_BTC"))

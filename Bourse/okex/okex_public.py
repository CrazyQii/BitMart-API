# -*- coding: utf-8 -*-
"""
okex spot public API
2020/10/14 hlq
"""
import requests
from datetime import datetime, timedelta
import traceback


class OkexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def _request(self, method, path, params=None, data=None, headers=None):
        try:
            resp = requests.request(method, path, params=params, data=data, headers=headers)

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

    def _output(self, function_name, content):
        info = {
            "func_name": function_name,
            "content": content
        }
        print(info)

    def get_price(self, symbol: str):
        """
        Get the latest trade price of the specified ticker
        """
        try:
            url = self.urlbase + "api/spot/v3/instruments/%s/ticker" % ('-'.join(symbol.split("_")))
            is_ok, content = self._request('GET', url)
            if is_ok:
                return float(content["last"])
            else:
                self._output('get_price', content)
                return None
        except Exception as e:
            print(e)
            return None

    def get_ticker(self, symbol: str):
        """
        Ticker is an overview of the market status of a trading pair,
        including the latest trade price, top bid and ask prices
        and 24-hour trading volume
        """
        try:
            url = self.urlbase + "api/spot/v3/instruments/%s/ticker" % ('-'.join(symbol.split("_")))
            is_ok, okex_content = self._request("GET", url)
            content = {}
            if is_ok:
                content = {
                    "symbol_id": symbol,
                    "url": url,
                    "base_volume": float(okex_content["base_volume_24h"]),
                    "volume": float(okex_content["quote_volume_24h"]),
                    "fluctuation": None,
                    "bid_1_amount": None,
                    "bid_1": float(okex_content["bid"]),
                    "ask_1_amount": None,
                    "ask_1": float(okex_content["ask"]),
                    "current_price": float(okex_content["last"]),
                    "lowest_price": float(okex_content["low_24h"]),
                    "highest_price": float(okex_content["high_24h"])
                }
            else:
                self._output("get_ticker", okex_content)
            return content
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol: str):
        """
        Get full depth of trading pairs.
        """
        try:
            url = self.urlbase + "api/spot/v3/instruments/%s/book" % ('-'.join(symbol.split("_")))
            is_ok, content = self._request('GET', url)
            orderbook = {
                'bids': [],
                'asks': []
            }
            if is_ok:
                orderbook = {
                    "bids": [[float(i[0]), float(i[1])] for i in content["bids"]],
                    "asks": [[float(i[0]), float(i[1])] for i in content["asks"]]
                }
            else:
                self._output('get_orderbook', content)
            return orderbook
        except Exception as e:
            print(e)
            return None

    def get_trades(self, symbol: str):
        """
        Get the latest trade records of the specified trading pair
        """
        try:
            url = self.urlbase + "api/spot/v3/instruments/%s/trades" % ('-'.join(symbol.split("_")))
            is_ok, okex_content = self._request("GET", url)
            content = []
            if is_ok:
                for trade in okex_content:
                    content.append({
                        "count": float(trade["size"]),
                        "amount": float(trade["size"]) * float(trade["price"]),
                        "type": trade["side"],
                        "price": float(trade["price"]),
                        "order_time": self._utc_to_ts(trade["timestamp"])
                    })
                return content
            else:
                self._output("get_trades", okex_content)
                return {"price": "0.0", "amount": "0.0"}
        except Exception as e:
            print(e)
            return None

    def get_kline(self, symbol: str, time_period=360):
        """
        Get k-line data within a specified time range of a specified trading pair
        """
        try:
            end = datetime.utcnow()
            start = end - timedelta(seconds=time_period)
            url = self.urlbase + "api/spot/v3/instruments/%s/candles?granularity=60&start=%sZ&end=%sZ" % (
                '-'.join(symbol.split("_")), start.isoformat(), end.isoformat())
            is_ok, okex_content = self._request("GET", url)
            content = []
            if is_ok:
                for line in okex_content:
                    content.append({
                        "timestamp": self._utc_to_ts(line[0]),
                        "volume": float(line[5]),
                        "open_price": float(line[1]),
                        "current_price": float(line[4]),
                        "lowest_price": float(line[3]),
                        "highest_price": float(line[2])
                    })
            else:
                self._output("get_kline", okex_content)
            return content
        except Exception as e:
            print(e)
            return None


if __name__ == "__main__":
    okex = OkexPublic("https://www.okex.com/")
    # print(okex.get_price("BTC_USDT"))
    # print(okex.get_ticker("BTC_USDT"))
    # print(okex.get_orderbook("BTC_USDT"))
    # print(okex.get_trades("BTC_USDT"))
    print(okex.get_kline("BTC_USDT"))

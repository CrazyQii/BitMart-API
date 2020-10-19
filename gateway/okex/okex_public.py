# -*- coding: utf-8 -*-
"""
okex spot public API
2020/10/14 hlq
"""
import requests
import math
from datetime import datetime, timedelta


class OkexPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def _symbol_convert(self, symbol: str):
        return '-'.join(symbol.split('_'))

    def _utc_to_ts(self, utc_time: str):
        Ymd, HMS = utc_time.split('T')
        t = f'{Ymd} {HMS[:-1]}'
        return round(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f').timestamp())

    def get_price_precision(self, symbol: str):
        try:
            url = self.urlbase + 'api/spot/v3/instruments'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp:
                    if ticker['instrument_id'] == self._symbol_convert(symbol):
                        return int(abs(math.log10(float(ticker['tick_size']))))
            else:
                print(f'Okex public error: {resp.json()["message"]}')
        except Exception as e:
            print(f'Okex public get price precision error: {e}')

    def get_price_increment(self, symbol: str):
        try:
            url = self.urlbase + 'api/spot/v3/instruments'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp:
                    if ticker['instrument_id'] == self._symbol_convert(symbol):
                        return float(ticker['tick_size'])
            else:
                print(f'Bitmart public error: {resp.json()["message"]}')
        except Exception as e:
            print(f'Bitmart public get price increment error: {e}')

    def get_amount_precision(self, symbol: str):
        try:
            url = self.urlbase + 'api/spot/v3/instruments'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp:
                    if ticker['instrument_id'] == self._symbol_convert(symbol):
                        return int(abs(math.log10(float(ticker['size_increment']))))
            else:
                print(f'Bitmart public error: {resp.json()["message"]}')
        except Exception as e:
            print("Bitmart public get amount precision error: %s" % e)

    def get_amount_increment(self, symbol: str):
        """
        minimum order quantity increment
        最小下单数量增量
        """
        try:
            url = self.urlbase + 'api/spot/v3/instruments'
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()
                for ticker in resp:
                    if ticker['instrument_id'] == self._symbol_convert(symbol):
                        return float(ticker['size_increment'])
            else:
                print(f'Bitmart public error: {resp.json()["message"]}')
        except Exception as e:
            print(f'Bitmart public get min amount error: {e}')

    def get_price(self, symbol: str):
        try:
            url = self.urlbase + f'api/spot/v3/instruments/{self._symbol_convert(symbol)}/ticker'
            resp = requests.get(url)
            price = 0.0
            if resp.status_code == 200:
                resp = resp.json()
                return float(resp['last'])
            else:
                print(f'Okex public request error: {resp.json()["message"]}')
            return price
        except Exception as e:
            print(f'Okex public get price error: {e}')

    def get_ticker(self, symbol: str):
        try:
            url = self.urlbase + f"api/spot/v3/instruments/{self._symbol_convert(symbol)}/ticker"
            resp = requests.get(url)
            ticker = {}
            if resp.status_code == 200:
                resp = resp.json()
                ticker = {
                    'symbol': resp['instrument_id'],
                    'last_price': float(resp['last']),
                    'quote_volume': float(resp['quote_volume_24h']),
                    'base_volume': float(resp['base_volume_24h']),
                    'highest_price': float(resp['high_24h']),
                    'lowest_price': float(resp['low_24h']),
                    'ask_1': float(resp['ask']),
                    'ask_1_amount': float(resp['best_ask_size']),
                    'bid_1': float(resp['bid']),
                    'bid_1_amount': float(resp['best_bid_size']),
                    'fluctuation': None,
                    'url': url
                }
            else:
                print(f'Okex public request error: {resp.json()["message"]}')
            return ticker
        except Exception as e:
                print(f'Okex public get ticker error: {e}')

    def get_orderbook(self, symbol: str):
        try:
            url = self.urlbase + f"api/spot/v3/instruments/{self._symbol_convert(symbol)}/book"
            resp = requests.get(url)
            orderbook = {'buys': [], 'sells': []}
            if resp.status_code == 200:
                resp = resp.json()
                for item in resp['bids']:
                    orderbook['buys'].append({
                        'amount': float(item[1]),
                        'total': None,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
                for item in resp['asks']:
                    orderbook['sells'].append({
                        'amount': float(item[1]),
                        'total': None,
                        'price': float(item[0]),
                        'count': int(item[2])
                    })
            else:
                print(f'Okex public request error: {resp.json()["message"]}')
            return orderbook
        except Exception as e:
            print(f'Okex public get orderbook error: {e}')

    def get_trades(self, symbol: str):
        try:
            url = self.urlbase + f"api/spot/v3/instruments/{self._symbol_convert(symbol)}/trades"
            resp = requests.get(url)
            trades = []
            if resp.status_code == 200:
                resp = resp.json()
                for trade in resp:
                    trades.append({
                        "amount": float(trade["size"]) * float(trade["price"]),
                        "order_time": self._utc_to_ts(trade["timestamp"]),
                        "price": float(trade["price"]),
                        "count": float(trade["size"]),
                        "type": trade["side"]
                    })
            else:
                print(f'Okex public request error: {resp.json()["message"]}')
            return trades
        except Exception as e:
            print(f'Okex public get trades error: {e}')

    def get_kline(self, symbol: str, time_period=360, interval=1):
        try:
            end = datetime.utcnow()
            start = end - timedelta(seconds=time_period)
            granularity = int(interval * 60)
            url = self.urlbase + f"api/spot/v3/instruments/{self._symbol_convert(symbol)}/candles?" \
                                 f"granularity={granularity}&start={start.isoformat()}Z&end={end.isoformat()}Z"
            resp = requests.get(url)
            lines = []
            if resp.status_code == 200:
                resp = resp.json()
                for line in resp:
                    lines.append({
                        "timestamp": self._utc_to_ts(line[0]),
                        "open": float(line[1]),
                        "high": float(line[2]),
                        "low": float(line[3]),
                        "volume": float(line[5]),
                        "last_price": float(line[4])
                    })
            else:
                print(f'Okex public request error: {resp.json()["message"]}')
            return lines
        except Exception as e:
            print(f'Okex public get kline error: {e}')


if __name__ == "__main__":
    okex = OkexPublic("https://www.okex.com/")
    # print(okex.get_price_precision('BTC_USDT'))
    # print(okex.get_price_increment('BTC_USDT'))
    # print(okex.get_amount_precision('BTC_USDT'))
    # print(okex.get_amount_increment('BTC_USDT'))
    print(okex.get_price("BTC_USDT"))
    print(okex.get_ticker("BTC_USDT"))
    print(okex.get_orderbook("BTC_USDT"))
    print(okex.get_trades("BTC_USDT"))
    print(okex.get_kline("BTC_USDT"))

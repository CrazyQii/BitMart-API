import requests
import os
import json


class XtPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

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
        pass

    def get_price(self, symbol):
        try:
            ticker = self.get_ticker(symbol)
            return ticker["current_price"]
        except Exception as e:
            print(e)
            return None

    def get_orderbook(self, symbol):
        try:
            url = "https://kline.xt.com/api/data/v1/entrusts?marketName=%s" % symbol
            response = requests.get(url)
            data = response.json()["datas"]
            buys, sells = [], []
            total_amount_buys = 0
            total_amount_sells = 0
            for i in data["bids"]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_buys += float(i[1])
                tmp["total"] = total_amount_buys
                buys.append(tmp)
            for i in data["asks"]:#[::-1]:
                tmp = {}
                tmp["price"] = i[0]
                tmp["amount"] = i[1]
                total_amount_sells += float(i[1])
                tmp["total"] = total_amount_sells
                sells.append(tmp)
            return {"buys": buys, "sells": sells[::-1]}
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
        url = "https://kline.xt.com/api/data/v1/ticker?marketName=%s" % symbol
        content = requests.request("GET", url)
        content = content.json()['datas']
        dict = {}
        dict['volume'] = content[4]
        dict['ask_1'] = content[8]
        dict['lowest_price'] = content[3]
        dict['bid_1'] = content[7]
        dict['highest_price'] = content[2]
        dict['base_volume'] = content[-1]
        dict['current_price'] = content[1]
        dict['fluctuation'] = content[5]
        dict['symbol_id'] = symbol
        return dict

    def get_trades(self, symbol):
        try:
            url = "https://kline.xt.com/api/data/v1/trades?marketName=%s&dataSize=20" % symbol
            response = requests.get(url)
            results = []
            for trade in response.json()["datas"]:
                results.append({
                    "count": trade[6],
                    "amount": float(trade[6]) * float(trade[5]),
                    "price": trade[5],
                    "type": "sell" if trade[4] == "ask" else "buy",
                    "order_time": trade[2]
                })
            return results
        except Exception as e:
            print(e)


if __name__ == "__main__":
    xt_public = XtPublic("")
    print(xt_public.get_price("HEX_USDT"))
    # print(xt_public.get_ticker("HEX_USDT"))
    # print(xt_public.get_orderbook("HEX_USDT"))
    # print(xt_public.get_precision("HEX_USDT"))
    # print(xt_public.get_quote_increment("HEX_USDT"))
    # print(xt_public.get_trades("HEX_USDT"))


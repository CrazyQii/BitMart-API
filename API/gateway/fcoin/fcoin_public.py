from os import sys, path
import os
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import json
import requests
import time

class FcoinPublic(object):
	def __init__(self, urlbase):
	    self.urlbase = urlbase

	def symbol_convert(self, symbol):
		return ''.join(symbol.split('_')).lower()

	def dump_json(self, data, file_name):
		try:
			path = os.path.join(os.path.split(os.path.realpath(__file__))[0], file_name)
			with open(path, "w+") as f:
				data_json = json.dumps(data, indent = 4)
				f.write(data_json)
			f.close()
		except Exception as e:
			print(e)

	def get_symbols_details(self):
		url = self.urlbase + "public/symbols"
		response = requests.get(url)
		data = response.json()["data"]
		self.dump_json(data, "fcoin_symbols_details.json")

	def load_symbols_details(self):
		try:
			current_path = os.path.dirname(os.path.abspath(__file__))
			symbols_details = {}
			with open(current_path + "/fcoin_symbols_details.json", "r") as f:
				symbols_details = json.load(f)
			f.close()
			return symbols_details
		except Exception as e:
			print (e)

	def get_precision(self, symbol):
		try:
			symbol = self.symbol_convert(symbol)
			symbols_details = self.load_symbols_details()
			details = next(item for item in symbols_details if item["name"] == symbol.lower())
			return int(details["price_decimal"])
		except Exception as e:
			print(e)

	def get_quote_increment(self, symbol):
		try:
			symbol = self.symbol_convert(symbol)
			symbols_details = self.load_symbols_details()
			details = next(item for item in symbols_details if item["name"] == symbol.lower())
			return float(1.0 / 10 ** details["price_decimal"])
		except Exception as e:
			print (e)

	def get_price(self, symbol):
		try:
			symbol = self.symbol_convert(symbol)
			url = self.urlbase + "market/ticker/%s" % symbol
			response = requests.get(url)
			return response.json()["data"]["ticker"][0]
		except Exception as e:
			print(e)

	def get_orderbook(self, symbol):
		try:
			symbol = self.symbol_convert(symbol)
			url = self.urlbase + "market/depth/L20/%s" % symbol
			response = requests.get(url)
			bids, asks = response.json()["data"]["bids"], response.json()["data"]["asks"]
			buys, sells = [], []
			buys_total, sells_total = 0, 0
			for i in range(int(len(bids) / 2)):
				buys_total += bids[2 * i + 1]
				buys.append({
					"price": bids[2 * i],
					"amount": bids[2 * i + 1],
					"total": buys_total 
					})
			for i in range(int(len(asks) / 2)):
				sells_total += asks[2 * i + 1]
				sells.append({
					"price": asks[2 * i],
					"amount": asks[2 * i + 1],
					"total": sells_total 
					})
			return {"buys": buys, "sells": sells}
		except Exception as e:
			print(e)

	def get_trades(self, symbol):
		try:
			symbol = self.symbol_convert(symbol)
			url = self.urlbase + "market/trades/%s?limit=20" % (symbol)
			response = requests.get(url)
			results = []
			for trade in response.json()["data"]:
				results.append({
					"count": trade["amount"], 
                    "amount": float(trade["amount"]) * float(trade["price"]), 
                    "price": trade["price"], 
                    "type": trade["side"], 
                    "order_time": trade["ts"]
					})
			return results
		except Exception as e:
			print (e)


if __name__ == "__main__":
	fp = FcoinPublic("https://api.fcoin.com/v2/")
	# fp.get_symbols_details()
	# print(fp.load_symbols_details())
	# print(fp.get_precision("ETH_USDT"))
	# print(fp.get_quote_increment("ETH_USDT"))
	# print(fp.get_price("BTC_USDT"))
	# print(fp.get_orderbook("BTC_USDT"))
	# print(fp.get_trades("BTC_USDT"))

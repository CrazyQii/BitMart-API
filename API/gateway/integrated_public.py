from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from gateway.binance.binance_public import BinancePublic
from gateway.huobi.huobi_public import HuobiPublic
from gateway.okex.okex_public import OkexPublic
from gateway.bibox.bibox_public import BiboxPublic
from gateway.cmc.cmc_public import CmcPublic
from gateway.coinbene.coinbene_public import CoinbenePublic
from gateway.coinis.coinis_public import CoinisPublic
from gateway.bitmart.bitmart_public import BitmartPublic
# from gateway.bitmart.ref_bitmart_public import RefBitMartPublic
from gateway.lbank.lbank_public import LbankPublic
from gateway.bitforex.bitforex_public import BitforexPublic
from gateway.bittrex.bittrex_public import BittrexPublic
from gateway.gateio.gateio_auth import GateioPublic
from gateway.idax.idax_public import IdaxPublic
from gateway.hotbit.hotbit_public import HotbitPublic
from gateway.hitbtc.hitbtc_public import HitbtcPublic
from gateway.bitz.bitz_public import BitzPublic
from gateway.coinzeus.coinzeus_public import CoinzeusPublic
from gateway.dragonex.ref_dragonex_public import RefDragonexPublic
from gateway.kucoin.ref_kucoin_public import RefKucoinPublic
from gateway.bw.bw_public import BwPublic
from gateway.fcoin.fcoin_public import FcoinPublic
from gateway.xt.xt_public import XtPublic
from gateway.http_data import get_price, get_orderbook
import json
import random
import requests
from constant.ref_symbols import *
from gateway.base_url import *
from config.limited_price import get_limited_price


class IntegratedPublic(object):
    def __init__(self):
        self.cmc_public = CmcPublic(cmc_base_url)
        self.ref_exchange_status = {}
        try:
            current_path = path.dirname(path.dirname(path.abspath(__file__)))
            with open(current_path + "/monitor/ref_exchange_status.json", "r") as f:
                self.ref_exchange_status = json.load(f)
            f.close()
        except Exception as e:
            print (e)

    def get_ref_exchange(self, symbol, ex):
        if symbol in binance_symbols and ex == "BNB":
            return "BNB"
        elif symbol in huobi_symbols and ex == "HB":
            return "HB"
        elif symbol in binance_symbols and ex == "binance":
            return BinancePublic(binance_base_url)
        elif symbol in okex_symbols and ex == "okex":
            return OkexPublic(okex_base_url)
        elif symbol in huobi_symbols and ex == "huobi":
            return HuobiPublic(huobi_base_url)
        elif symbol in hitbtc_symbols and ex == "hitbtc":
            return HitbtcPublic(hitbtc_base_url)
        elif symbol in fcoin_symbols and ex == "fcoin":
            return FcoinPublic(fcoin_base_url)
        elif symbol in bittrex_symbols and ex == "bittrex":
            return BittrexPublic(bittrex_base_url)
        elif symbol in bibox_symbols and ex == "bibox":
            return BiboxPublic(bibox_base_url)
        elif symbol in lbank_symbols and ex == "lbank":
            return LbankPublic(lbank_base_url)
        elif symbol in bitz_symbols and ex == "bitz":
            return BitzPublic(bitz_base_url)
        elif symbol in bw_symbols and ex == "bw":
            return BwPublic(bw_base_url)
        elif symbol in coinbene_symbols and ex == "coinbene":
            return CoinbenePublic(coinbene_base_url)
        elif symbol in coinzeus_symbols and ex == "coinzeus":
            return CoinzeusPublic(coinzeus_base_url)
        elif symbol in coinis_symbols and ex == "coinis":
            return CoinisPublic(coinis_base_url)
        elif symbol in bitmart_symbols and ex == "bitmart":
            return BitmartPublic(bitmart_base_url_production)
        # elif symbol in missionx_symbols and ex == "missionx":
        #     return RefBitmartPublic(bitmart_base_url_production)
        # elif symbol in ref_bitmart_symbols and ex == "refbitmart":
        #     return RefBitmartPublic(bitmart_base_url_production)
        elif symbol in bitforex_symbols and ex == "bitforex":
            return BitforexPublic(bitforex_base_url)
        elif symbol in gateio_symbols and ex == "gateio":
            return GateioPublic(gateio_base_url)
        elif symbol in hotbit_symbols and ex == "hotbit":
            return HotbitPublic(hotbit_base_url)
        elif symbol in idax_symbols and ex == "idax":
            return IdaxPublic(idax_base_url)
        elif symbol in ref_kucoin_symbols and ex == "refkucoin":
            return RefKucoinPublic(kucoin_base_url)
        elif symbol in ref_dragonex_symbols and ex == "refdragonex":
            return RefDragonexPublic(dragonex_base_url)
        elif symbol in xt_symbols and ex == "xt":
            return XtPublic(xt_base_url)
        # else:
        #     return self.cmc_public

    # def get_ref_limited_price(self, symbol, limited_price_json):
    #     try:
    #         symbol_pair = re.findall("[A-Z]+", symbol)
    #         symbol_base = symbol_pair[0]
    #         symbol_quote = symbol_pair[1]
    #         bitmart_public = BitmartPublic(bitmart_base_url_production)
    #         if symbol_base + "_ETH" in limited_price_json.keys():
    #             price_lower = float(limited_price_json[symbol_base + "_ETH"]["price_lower"])
    #             price_upper = float(limited_price_json[symbol_base + "_ETH"]["price_upper"])
    #             price_quote_pair = float(bitmart_public.get_price("ETH_" + symbol_quote))
    #             return (price_lower * price_quote_pair, price_upper * price_quote_pair)
    #         elif symbol_base + "_BTC" in limited_price_json.keys():
    #             price_lower = float(limited_price_json[symbol_base + "_BTC"]["price_lower"])
    #             price_upper = float(limited_price_json[symbol_base + "_BTC"]["price_upper"])
    #             if symbol_quote == "ETH":
    #                 price_quote_pair = float(bitmart_public.get_price("ETH_BTC"))
    #                 return (price_lower / price_quote_pair, price_upper / price_quote_pair)
    #             elif symbol_quote == "USDT":
    #                 price_quote_pair = float(bitmart_public.get_price("BTC_USDT"))
    #                 return (price_lower * price_quote_pair, price_upper * price_quote_pair)
    #         elif symbol_base + "_USDT" in limited_price_json.keys():
    #             price_lower = float(limited_price_json[symbol_base + "_USDT"]["price_lower"])
    #             price_upper = float(limited_price_json[symbol_base + "_USDT"]["price_upper"])
    #             price_quote_pair = float(bitmart_public.get_price(symbol_quote + "_USDT"))
    #             return (price_lower / price_quote_pair, price_upper / price_quote_pair)
    #         else:
    #             return (None, None)

    #     except Exception as e:
    #         print(e)

    # def get_limited_price(self, symbol):
    #     try:
    #         current_path = path.dirname(path.dirname(path.abspath(__file__)))
    #         limited_price_json = {}
    #         with open(current_path + "/config/limited_price.json", "r") as f:
    #             limited_price_json = json.load(f)
    #         f.close()
    #         if symbol not in limited_price_json.keys():
    #             return self.get_ref_limited_price(symbol, limited_price_json)

    #         price_lower = float(limited_price_json[symbol]["price_lower"])
    #         price_upper = float(limited_price_json[symbol]["price_upper"])
    #         return (price_lower, price_upper)
    #     except Exception as e:
    #         print(e)

    def get_price(self, symbol):
        try:
            ref_price = None
            for ex in ["binance", "huobi", "okex", "hitbtc", "fcoin", "bittrex", "bibox", "lbank", "bitz", "bw", "coinbene", "coinzeus",
                "coinis", "bitmart", "bitforex", "gateio", "hotbit", "idax", "refkucoin", "refdragonex", "xt"]:
                ref_exchange = self.get_ref_exchange(symbol, ex)
                if ref_exchange:
                    try:
                        if ex == "BNB":
                            ref_price = get_price("BNB", symbol)
                        elif ex == "HB":
                            ref_price = get_price("HB", symbol)
                        else:
                            ref_price = ref_exchange.get_price(symbol)
                    except Exception as e:
                        print(e)
                        return 0
                    if ref_price:
                        print ("The current ref_price of %s  %s is: %s." % (ex, symbol, ref_price))
                        break
            if ref_price is not None:
                ref_price = float(ref_price)
            # ref_exchange = self.get_ref_exchange(symbol)
            # ref_price = ref_exchange.get_price(symbol)
            # # print(ref_price, ref_exchange)
            # print ("The current ref_price of %s is: %s." % (symbol, ref_price))
            if symbol in price_limit_symbols:
                limited_price = get_limited_price(symbol)
                price_upper = limited_price["price_upper"]
                price_lower = limited_price["price_lower"]
                if ref_price >= price_upper:
                    ref_price = price_upper - (price_upper - price_lower) * random.uniform(0, 0.1)
                    print ("the ref_price has been redirected to limited_price: %s." % (ref_price))
                elif ref_price <= price_lower:
                    ref_price = price_lower + (price_upper - price_lower) * random.uniform(0, 0.1)
                    print ("the ref_price has been redirected to limited_price: %s." % (ref_price))
            if ref_price is not None:
                return ref_price
            self.bitmart_public = BitmartPublic(bitmart_base_url_production)
            # ref_price = self.bitmart_public.get_price(symbol)
            # print("%s  ref price %s" % (symbol, ref_price))
            # return ref_price
            return self.cmc_public.get_price(symbol)
        except Exception as e:
            print(e)
            return 0

    def get_bm_price(self, symbol):
        try:
            bitmart_price = 0
            self.bitmart_public = BitmartPublic(bitmart_base_url_production)
            bitmart_price = get_price("BM", symbol)
            if bitmart_price == 0:
                bitmart_price = float(self.bitmart_public.get_price(symbol))
                print ("The current price of bitmart  %s is: %s." % (symbol, bitmart_price))
            else:
                print ("The current price of BM  %s is: %s." % (symbol, bitmart_price))
            return bitmart_price
        except Exception as e:
            print(e)
            return 0

    def get_orderbook(self, symbol):
        ref_orderbook = {}
        try:
            for ex in ["binance", "huobi", "okex", "hitbtc", "fcoin", "bittrex", "bibox", "lbank", "bitz", "bw", "coinbene", "coinzeus",
                "coinis", "bitmart", "bitforex", "gateio", "hotbit", "idax", "refkucoin", "refdragonex", "xt"]:
                ref_exchange = self.get_ref_exchange(symbol, ex)
                if ref_exchange:
                    try:
                        if ex == "BNB":
                            ref_orderbook = get_orderbook("BNB", symbol)
                        elif ex == "HB":
                            ref_orderbook = get_orderbook("HB", symbol)
                        else:
                            ref_orderbook = ref_exchange.get_orderbook(symbol)
                    except Exception as e:
                        print(e)
                        
                    if ref_orderbook:
                        # print ("The current ref_orderbook of %s  %s is: %s." % (ex, symbol, ref))
                        break
            if ref_orderbook is not None:
                print("The current ref_orderbook %s %s is ready!" % (ex, symbol))
                return ref_orderbook
            return ref_orderbook
        except Exception as e:
            print(e)
            return ref_orderbook

    def get_kline(self, symbol):
        kline = []
        try:
            for ex in ["binance", "huobi", "okex", "hitbtc", "fcoin", "bittrex", "bibox", "lbank", "bitz", "bw", "coinbene", "coinzeus",
                "coinis", "bitmart", "bitforex", "gateio", "hotbit", "idax", "refkucoin", "refdragonex", "xt"]:
                ref_exchange = self.get_ref_exchange(symbol, ex)
                if ref_exchange:
                    try:
                        kline = ref_exchange.get_kline(symbol)
                    except Exception as e:
                        print(e)
                    if kline:
                        break
            if kline is not None:
                print("The current kline %s %s is ready!" % (ex, symbol))
                return kline
            return kline
        except Exception as e:
            print(e)
            return kline

    def get_hex_price(self, symbol):
        ref_price = 0
        url = "https://uniswapdataapi.azurewebsites.net/api/hexPrice"
        ret = requests.get(url)
        if ret.status_code == 200:
            data = json.loads(ret.text)
            if symbol == "HEX_USDT":
                ref_price = float(data["hexUsd"])
            elif symbol == "HEX_BTC":
                ref_price = float(data["hexBtc"])
            elif symbol == "HEX_ETH":
                ref_price = float(data["hexEth"])
        print ("The current price of uniswap %s is: %s." % (symbol, ref_price))
        return ref_price
        #{"lastUpdated":"2020-04-19T01:50:45","hexEth":"0.0000074863","hexUsd":"0.0013993051","hexBtc":"0.0000001933"}
    # def get_price_factor(self):
    #     binance_public = BinancePublic(binance_base_url)
    #     btc_price = binance_public.get_price("BTC_USDT")
    #     eth_price = binance_public.get_price("ETH_USDT")
    #     xrp_price = binance_public.get_price("XRP_USDT")
    #     eos_price = binance_public.get_price("EOS_USDT")
    #     factor = 0.60 * btc_price / 3750 + 0.20 * eth_price / 145 + 0.1 * xrp_price / 0.35 + 0.1 * eos_price / 2.6
    #     return factor

if __name__ == "__main__":
    integrated = IntegratedPublic()
    # print (integrated.ref_exchange_status)
    # print integrated.get_price("RHOC_ETH")
    # print integrated.get_price("RHOC_BTC")
    # print (integrated.get_hex_price("HEX_USDT"))
    # print (integrated.get_price("EOS_USDT"))
    # print (integrated.get_price("HT_USDT"))
    # print (integrated.get_price("BSV_USDT"))
    # print(integrated.get_bm_price("BTC_USDT"))
    # print(integrated.get_bm_price("BMX_USDT"))
    # print(integrated.get_bm_price("EOS_BTC"))
    # print integrated.get_price("GXC_BTC")
    # print (integrated.get_price("BTC_PAX"))
    # print integrated.get_price_factor()
    # print integrated.get_price("WPC_BTC")
    # print(integrated.get_orderbook("EOS_USDT"))
    print(integrated.get_kline("EOS_USDT"))

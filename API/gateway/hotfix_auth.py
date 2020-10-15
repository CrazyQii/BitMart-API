from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from bitmart.bitmart_auth import BitMartAuth
from Bourse.bitmart.bitmart_public import BitMartPublic
from key import bitmart_token_production

from constant.base_url import bitmart_base_url_production
import re
import random
import time


def fix_price(price, digit=6):
        return int(price*(10**digit))/(10**digit)

def fix_amount(amount, digit=6):
    return int(amount*(10**digit))/(10**digit)

if __name__ == "__main__":

    # while True:
    #     try:
    #         #20200304
    #         # trading yaofund.
    #         # BMX_BTC 交易前 base1 11734588.2,  qoute1 17.3132215771
    #         # BMX_ETH 交易前 base1 11734588.2,  qoute1 32.5443074724
    #         # BMX_USDT 交易前 base1 11734588.2,  qoute1 949976.3646833563
    #         # trading wangdongdong.
    #         # BMX_BTC 交易前 base1 5000000.7109,  qoute1 0.000733905
    #         # BMX_ETH 交易前 base1 5000000.7109,  qoute1 330.2530797516
    #         # BMX_USDT 交易前 base1 5000000.7109,  qoute1 65.9
    #         # trading 2018.
    #         # BMX_BTC 交易前 base1 2857818.4,  qoute1 0.5007584846
    #         # BMX_ETH 交易前 base1 2857818.4,  qoute1 448.120039781
    #         # BMX_USDT 交易前 base1 2857818.4,  qoute1 1096.2094
    #         # trading bluerry.
    #         # BMX_BTC 交易前 base1 5215967.3,  qoute1 0.285094117
    #         # BMX_ETH 交易前 base1 5215967.3,  qoute1 362.830766064
    #         # BMX_USDT 交易前 base1 5215967.3,  qoute1 1069.41091
    #         # trading ox2048.
    #         # BMX_BTC 交易前 base1 5000000.8,  qoute1 0.447383676
    #         # BMX_ETH 交易前 base1 5000000.8,  qoute1 421.1814352106
    #         # BMX_USDT 交易前 base1 5000000.8,  qoute1 7592.59921
    #         # trading aristotle.
    #         # BMX_BTC 交易前 base1 4993720.07577,  qoute1 0.000945912
    #         # BMX_ETH 交易前 base1 4993720.07577,  qoute1 0.0072765258
    #         # BMX_USDT 交易前 base1 4993720.07577,  qoute1 89679.99204
    #         # trading yosemite.
    #         # BMX_BTC 交易前 base1 5000000.5,  qoute1 0.009395711
    #         # BMX_ETH 交易前 base1 5000000.5,  qoute1 0.029291373
    #         # BMX_USDT 交易前 base1 5000000.5,  qoute1 109763.63683
    #         # trading bmfund.
    #         # BMX_BTC 交易前 base1 14607943.3389,  qoute1 0.0910804271
    #         # BMX_ETH 交易前 base1 14590927.6389,  qoute1 0.000610589
    #         # BMX_USDT 交易前 base1 14607299.3389,  qoute1 29.0988868
    #         # trading kelvin.
    #         # BMX_BTC 交易前 base1 7750124.7,  qoute1 0.1109848465
    #         # BMX_ETH 交易前 base1 7750124.7,  qoute1 3.4833079541
    #         # BMX_USDT 交易前 base1 7750124.7,  qoute1 5.74e-05
    #         # trading xia909.
    #         # BMX_BTC 交易前 base1 24198509.454889096,  qoute1 1.016408224
    #         # BMX_ETH 交易前 base1 24198509.454889096,  qoute1 1.9550717732
    #         # BMX_USDT 交易前 base1 24198509.454889096,  qoute1 48989.3460381267
    #     ######################交易大赛#####################
    #         token1, secret1 = bitmart_token_production.get_token_yaofund_prod()  #btc:62.7293443381  eth:724.2226157274  usdt:417000.5319730840 BMX:15465239.
    #         token2, secret2 = bitmart_token_production.get_token_bmfund_prod()#btc:0.0003703761  eth:93.4537924490  usdt:51459.6281768 BMX:5838734.838
    #         token3, secret3 = bitmart_token_production.get_token_wangdongdong_prod()  #11105490.7000000000  49.6791450671  384575.9186515400
    #         token4, secret4 = bitmart_token_production.get_token_tytrading2018_prod()  #btc:0.3122674216  eth:11.5025875670  usdt:30840.90558 BMX:1156999# 1805180.5000000000  1.7250920476   10992.1188300000
    #         token5, secret5 = bitmart_token_production.get_token_blueberry_prod()  #btc:1.629139  eth:96.4912028  usdt:24838.67 BMX:94539.3#  2136723.4000000000   1.1024860980   14360.8156500000
    #         token6, secret6 = bitmart_token_production.get_token_ox2048_prod() # btc:0  eth:578  usdt:52  BMX:5000000
    #         token7, secret7 = bitmart_token_production.get_token_aristotle_prod() # btc:0  eth:0  usdt:94199.79  BMX:5000000 
    #         token8, secret8 = bitmart_token_production.get_token_yosemite_prod() #btc:0  eth:0  usdt:117190.87  BMX:5000000
    #         token9, secret9 = bitmart_token_production.get_token_kelvin_prod()#btc:3.2158  eth:17  usdt:0  BMX:466164
    #         token10, secret10 = bitmart_token_production.get_token_xia909_prod()#btc:0  eth:0  usdt:80000  BMX:30000000

    #         # key_list = [(token1, secret1),(token3, secret3), (token4, secret4),(token5, secret5),(token6, secret6), (token7, secret7), (token8, secret8), (token2, secret2), (token9, secret9), (token10, secret10)]
    #         key_list = [(token7, secret7), (token8, secret8), (token9, secret9)]
            
    #         for key in key_list:
    #             bitmart_public = BitMartPublic(bitmart_base_url_production)
    #             bitmart1 = BitMartAuth(bitmart_base_url_production, key[0], key[1])
    #             # bitmart2 = BitMartAuth(bitmart_base_url_production, token1, secret1)
    #             key_index = key_list.index(key)
    #             # if key_index == 0:
    #             #     amount1, amount2 = 50000, 400000
    #             #     print("trading yaofund.")
    #             # elif key_index == 1:
    #             #     amount1, amount2 = 50000, 500000
    #             #     print("trading wangdongdong.")
    #             # elif key_index == 2:
    #             #     amount1, amount2 = 50000, 500000
    #             #     print("trading 2018.")
    #             # elif key_index == 3:
    #             #     amount1, amount2 = 50000, 500000
    #             #     print("trading bluerry.")
    #             # elif key_index == 4:
    #             #     amount1, amount2 = 50000, 500000
    #             #     print("trading ox2048.")
    #             if key_index == 0:
    #                 amount1, amount2 = 100000, 500000
    #                 print("trading aristotle.")
    #             elif key_index == 1:
    #                 amount1, amount2 = 50000, 500000
    #                 print("trading yosemite.")
    #             # elif key_index == 7:
    #             #     amount1, amount2 = 50000, 500000
    #             #     print("trading bmfund.")
    #             elif key_index == 2:
    #                 amount1, amount2 = 100000, 500000
    #                 print("trading kelvin.")
    #             # elif key_index == 9:
    #             #     amount1, amount2 = 50000, 500000
    #             #     print("trading xia909.")
    #             # if key_index == 7:
    #             #     order1 = bitmart1.place_order("BMX_BTC", 1000, 0.00000150, "sell")
    #             #     order1 = bitmart1.place_order("BMX_ETH", 1000, 0.0000850, "sell")
    #             # balance1, frozen1 = bitmart1.wallet_balance()
    #             # print(balance1["BMX"])
    #             # print(balance1["BTC"])
    #             # print(balance1["ETH"])
    #             # print(balance1["USDT"])
    #             # print("--------")
                
    #             for i in range(3):
    #                 for symbol in ["BMX_BTC", "BMX_ETH", "BMX_USDT"]:

    #                     buy_sell_1 = "buy"
    #                     buy_sell_2 = "sell"

    #                     if symbol == "BMX_USDT":
    #                         price_digit = 4
    #                         price_step = 0.0001
    #                     else:
    #                         price_digit = 8
    #                         price_step = 0.00000001
    #                     amount_digit = 1

    #                     symbol_pair = re.findall("[A-Z]+", symbol)
    #                     symbol_base = symbol_pair[0]
    #                     symbol_quote = symbol_pair[1]

    #                     order_list = bitmart1.open_orders(symbol)
    #                     #print(order_list)
    #                     for order in order_list:
    #                         if float(order["original_amount"]) > 50000:
    #                             bitmart1.cancel_order(order["entrust_id"])
                        
    #                     orderbook = bitmart_public.get_orderbook(symbol)
    #                     trades = bitmart_public.get_trades(symbol)
    #                     last_price = float(trades[-1]["price"])
    #                     ask = float(orderbook["sells"][0]["price"])
    #                     bid = float(orderbook["buys"][0]["price"])
    #                     if ask - bid <= price_step:
    #                         print("%s step too small" % symbol)
    #                         #continue
    #                     if ask != 0 and bid != 0:
    #                         if random.random() < 0.6:
    #                             sum = 6 * ask + 4 * bid
    #                             price = sum/10
    #                         else:
    #                             sum = ask + bid
    #                             price = sum/2
    #                         # if ask - bid < 1 * price_step:
    #                         #     print("价差太少")
    #                         #     continue

    #                         balance1, frozen1 = bitmart1.wallet_balance()
                            
    #                         base_balance1 = float(balance1[symbol_base])
    #                         qoute_balance1= float(balance1[symbol_quote])
    #                         print("%s 交易前 base1 %s,  qoute1 %s" % (symbol, base_balance1, qoute_balance1))
    #                         if base_balance1 < 100000:
    #                             print("资金余额不足")
    #                             continue
    #                             # if symbol_quote == "BTC":
    #                             #     if qoute_balance1 > 3:
    #                             #         order = bitmart1.place_order("BMX_BTC", 500000, ask, buy_sell_1)
    #                             #         print("buy btc bmx")
    #                             #         bitmart1.cancel_order(order)
    #                             # elif symbol_quote == "ETH":
    #                             #     if qoute_balance1 > 200:
    #                             #         order = bitmart1.place_order("BMX_ETH", 500000, ask, buy_sell_1)
    #                             #         print("buy eth bmx")
    #                             #         bitmart1.cancel_order(order)
    #                             # if symbol_quote == "USDT":
    #                             #     if qoute_balance1 > 30000:
    #                             #         order = bitmart1.place_order("BMX_USDT", 500000, ask, buy_sell_1)
    #                             #         print("buy usdt bmx")
    #                             #         bitmart1.cancel_order(order)
    #                         # else:
    #                         #     if float(balance1["BTC"]) < 2 and float(balance1["USDT"]) < 20000 and float(balance1["ETH"]) < 100:
    #                         #         if symbol_quote == "USDT":
    #                         #             order = bitmart1.place_order("BMX_USDT", 300000, bid, buy_sell_1)
    #                         #             print("sell usdt bmx")
    #                         #             bitmart1.cancel_order(order)

    #                         if symbol_quote == "BTC":
    #                             if qoute_balance1 < 0.2:
    #                                 print("%s 资金余额不足" % symbol_quote)
    #                                 continue
    #                         if symbol_quote == "ETH":
    #                             if qoute_balance1 < 10:
    #                                 print("%s 资金余额不足" % symbol_quote)
    #                                 continue
    #                         if symbol_quote == "USDT":
    #                             if qoute_balance1 < 2000:
    #                                 print("%s 资金余额不足" % symbol_quote)
    #                                 continue
    #                         price = round(price, price_digit)
    #                         price = fix_price(price, digit=price_digit)
    #                         amount = random.randint(amount1, amount2)
    #                         amount= fix_amount(amount, digit=amount_digit)
                            
    #                         if abs(price - last_price)/last_price > 0.05:
    #                             print("price abnormal!")
    #                             continue
    #                         if buy_sell_1 == "buy" and buy_sell_2 == "sell":
    #                             if qoute_balance1 >= amount * price and amount < base_balance1:
    #                                 if random.random() < 0.5:
    #                                     order1 = bitmart1.place_order(symbol, amount, price, buy_sell_1)
    #                                     order2 = bitmart1.place_order(symbol, amount, price, buy_sell_2)
    #                                 else:
    #                                     order2 = bitmart1.place_order(symbol, amount, price, buy_sell_2)
    #                                     order1 = bitmart1.place_order(symbol, amount, price, buy_sell_1)
    #                                 print("trading base %s   qoute %s" % (amount, amount*price))
    #                                 #time.sleep(1)
    #                                 orderinfo1 = bitmart1.order_detail(order1)
    #                                 orderinfo2 = bitmart1.order_detail(order2)
    #                                 print(orderinfo1)
    #                                 print(orderinfo2)

    #                                 print(bitmart1.cancel_order(order1))
    #                                 print(bitmart1.cancel_order(order2))
    #                             else:
    #                                 print("buy sell amount no equal.")
    #                     order_list = bitmart1.open_orders(symbol)
    #                     #print(order_list)
    #                     for order in order_list:
    #                         if float(order["original_amount"]) > 50000:
    #                             bitmart1.cancel_order(order["entrust_id"])
    #                     time.sleep(random.randint(1, 3))
    #     except Exception as e:
    #         print(e)
    #     #########################交易大赛##########################
    while True:
        try:
            for symbol in ["BTC_USDT"]:
                amount_digit= 5 #amount_dight_symbols[symbol]
                price_digit = 2 #price_dight_symbols[symbol]
                
                if symbol == "BTC_USDT":
                    token1, secret1 = bitmart_token_production.get_token_btc_usdt_prod()

                symbol_pair = re.findall("[A-Z]+", symbol)
                symbol_base = symbol_pair[0]
                symbol_quote = symbol_pair[1]
                bitmart_public = BitMartPublic(bitmart_base_url_production)
                bitmart1 = BitMartAuth(bitmart_base_url_production, token1, secret1)
                for i in range(15):
                    balance1, frozen1 = bitmart1.wallet_balance()
                    base_balance1 = float(balance1[symbol_base])
                    qoute_balance1= float(balance1[symbol_quote])
                    price = float(bitmart_public.get_price(symbol))
                    price = fix_price(price, digit=price_digit)
                    orderbook = bitmart_public.get_orderbook(symbol)
                    ask1 = float(orderbook["sells"][1]["price"])
                    bid1 = float(orderbook["buys"][1]["price"])

                    if symbol == "BTC_USDT":
                        btc_amount = float(balance1["BTC"]) + float(frozen1["BTC"])
                        usdt_amount= float(balance1["USDT"])+ float(frozen1["USDT"])
                        print("BTC: %s  USDT: %s Price: %s" % (btc_amount, usdt_amount, price))
                        amount = round(random.uniform(0.05, 0.3), 5)
                        if 5500 < ask1 <= 6000:
                            if btc_amount < 70:
                                order_id000 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail000 = bitmart1.order_detail(order_id000)
                                print(order_detail000)
                                time.sleep(1)
                                order_cancel000 = bitmart1.cancel_order(order_id000)
                                print(order_cancel000)
                        elif 5400 < ask1 <= 5500:
                            if btc_amount < 80:
                                order_id00 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail00 = bitmart1.order_detail(order_id00)
                                print(order_detail00)
                                time.sleep(1)
                                order_cancel00 = bitmart1.cancel_order(order_id00)
                                print(order_cancel00)
                        elif 5200 < ask1 <= 5400:
                            if btc_amount < 85:
                                order_id0 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail0 = bitmart1.order_detail(order_id0)
                                print(order_detail0)
                                time.sleep(1)
                                order_cancel0 = bitmart1.cancel_order(order_id0)
                                print(order_cancel0)
                        elif 5000 < ask1 <= 5200:
                            if btc_amount < 90:
                                order_id1 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail1 = bitmart1.order_detail(order_id1)
                                print(order_detail1)
                                time.sleep(1)
                                order_cancel1 = bitmart1.cancel_order(order_id1)
                                print(order_cancel1)
                        elif 4500 < ask1 <= 5000:
                            if btc_amount < 100:
                                order_id2 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail2 = bitmart1.order_detail(order_id2)
                                print(order_detail2)
                                time.sleep(1)
                                order_cancel2 = bitmart1.cancel_order(order_id2)
                                print(order_cancel2)
                        elif 4000 < ask1 <= 4500:
                            if btc_amount < 150:
                                order_id3 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail3 = bitmart1.order_detail(order_id3)
                                print(order_detail3)
                                time.sleep(1)
                                order_cancel3 = bitmart1.cancel_order(order_id3)
                                print(order_cancel3)
                        elif 3500 < ask1 <= 4000:
                            if btc_amount < 180:
                                order_id4 = bitmart1.place_order(symbol, amount, ask1, "buy")
                                order_detail4 = bitmart1.order_detail(order_id4)
                                print(order_detail4)
                                time.sleep(1)
                                order_cancel4 = bitmart1.cancel_order(order_id4)
                                print(order_cancel4)
                        if bid1 > 9000:
                            if btc_amount > 200:
                                order_id5 = bitmart1.place_order(symbol, amount, bid1, "sell")
                                order_detail5 = bitmart1.order_detail(order_id5)
                                print(order_detail5)
                                time.sleep(1)
                                order_cancel15 = bitmart1.cancel_order(order_id5)
                                print(order_detail5)
        except Exception as e:
            print(e)

    # token = bitmart_token_production.get_token_apl_prod()
    # token, secret = bitmart_token_production.get_token_lee_prod()
    # token1 = bitmart_token_production.get_token_boxcapital_prod()
    # print bitmart_token_production.get_token_mgc_prod()
    # token, secret = bitmart_token_production.get_token_afund_prod()
    # hotfix = BitMartAuth(bitmart_base_url_production, token, secret)
    # # hotfix.cancel_all("EOS_USDT", "buy")
    # # hotfix.cancel_all("EOS_USDT", "sell")
    # a, b = (hotfix.wallet_balance())
    # print ("BTC:", float(a["BTC"]) + float(b["BTC"]))
    # print ("ETH:", float(a["ETH"]) + float(b["ETH"]))
    # print ("USDT:", float(a["USDT"]) + float(b["USDT"]))
    # print("EOS:", float(a["EOS"]) + float(b["EOS"]))


    # order1 = hotfix.place_order("ETH_USDT", 10, 211, "buy")
    # order2 = hotfix.place_order("ATOM_BTC", 20, 0.0003765, "buy")
    # hotfix.cancel_order(616751394)
    # hotfix.cancel_all("GNT_ETH", "buy")
    # hotfix.cancel_all("GNT_BTC", "buy")

    # order1 = hotfix.place_order("BMX_BTC", 200000, 0.00000235, "buy")
    # order2 = hotfix.place_order("GNY_BTC", 574, 0.00000816, "buy")
    # hotfix.cancel_order(order1)
    # hotfix.cancel_order(order2)
    # hotfix.cancel_all("BMX_BTC", "buy")
    # order2 = hotfix.place_order("GNY_BTC", 5100, 0.0000081, "buy")
    # hotfix.cancel_all("BMX_ETH", "sell")
    # hotfix.cancel_all("BMX_BTC", "sell")
    # hotfix.cancel_all("MBIT_ETH", "sell")
    # hotfix.cancel_all("MBIT_ETH", "buy")

    # hotfix = BitMartAuth(bitmart_base_url_production, token, secret)
    # hotfix.place_order("NNC_ETH", 23107, 0.000097, "sell")
    # hotfix.place_order("NNC_ETH", 27211, 0.000091, "sell")
    # hotfix.place_order("NNC_ETH", 34281, 0.000096, "sell")
    # hotfix.place_order("NNC_ETH", 31812, 0.000093, "sell")
    # hotfix.place_order("NNC_ETH", 22732, 0.000096, "sell")
    # hotfix.place_order("NNC_ETH", 21300, 0.000080, "sell")
    # hotfix.place_order("NNC_ETH", 24200, 0.000090, "sell")
    # hotfix.place_order("ETH_BTC", 50, 0.034430, "buy")
    # hotfix.cancel_all("ETH_BTC", "buy")

    # hotfix.place_order("MBIT_ETH", 2000, 0.00007, "sell")

    # boxcapital = BitMartAuth(bitmart_base_url_production, token1)


    # order1 = hotfix.place_order("ETH_BTC", 10, 0.040722, "buy")
    # order2 = boxcapital.place_order("ETH_BTC", 10, 0.040722, "sell")
    # hotfix.cancel_order(order1)
    # boxcapital.cancel_order(order2)
    # order2 = bitmart2.place_order("XLM_USDT", 80000, 0.16063393, "buy")


    # hotfix.cancel_all("SNPC_BTC", "sell")
    # hotfix.cancel_all("SNPC_BTC", "buy")
    # hotfix.cancel_all("OMG_BMX", "sell")
    # hotfix.cancel_all("OMG_BMX", "buy")
    # hotfix.cancel_all("VET_BMX", "sell")
    # hotfix.cancel_all("VET_BMX", "buy")


    # token = bitmart_token_production.get_token_bob_prod()
    # hotfix = BitMartAuth(bitmart_base_url_production, token)
    # hotfix.cancel_order("126062624")
    # hotfix.place_order("APL_ETH", 16, 0.00000548, "sell")
    # hotfix.place_order("BOB_ETH", 6000, 0.000110, "buy")
    # num = random.randint(1000, 3000)
    # price = 0.00008050
    # hotfix.place_order("LXT_ETH", num, price, "sell")
    # hotfix.place_order("LXT_ETH", num, price, "buy")
    # print hotfix.order_detail("62166475")
    # print hotfix.wallet_balance()
    # print (hotfix.in_order_list("LXT_ETH"))

    # token = bitmart_token_production.get_token_one_prod()
    # hotfix = BitMartAuth(bitmart_base_url_production, token)
    # num = random.randint(1000, 3000)
    # price = 0.00002241
    # hotfix.place_order("ONE_ETH", num, price, "sell")
    # hotfix.place_order("ONE_ETH", num, price, "buy")

    # token = bitmart_token_production.get_token_xia_prod()
    # hotfix = BitMartAuth(bitmart_base_url_production, token)
    # num = random.randint(1000, 3000)
    # price = 0.00007150
    # hotfix.place_order("LXT_ETH", num, price, "sell")
    # hotfix.place_order("LXT_ETH", num, price, "buy")
    # token = get_token_xia_prod()
    # hotfix = BitMartAuth(bitmart_base_url_production, token)
    # hotfix.cancel_all("BTM_ETH", "sell")
    # hotfix.cancel_all("BTM_ETH", "buy")
    # hotfix.cancel_all("BTM_BTC", "sell")
    # hotfix.cancel_all("BTM_BTC", "buy")


    # XRP / BTC
    # token1, secret1 = bitmart_token_production.get_token_lee_prod()
    # token2, secret2 = bitmart_token_production.get_token_bmfund_prod()
    # bitmart1 = BitMartAuth(bitmart_base_url_production, token1, secret1)
    # bitmart2 = BitMartAuth(bitmart_base_url_production, token2, secret2)

    # order1 = bitmart1.place_order("BMX_ETH", 200000.7369, 0.00018572 , "buy")
    # order2 = bitmart2.place_order("BMX_ETH", 200000.7369, 0.00018572, "sell")

    # btc usdt
    # token1,secret1 = bitmart_token_production.get_token_yao_prod()
    # token2,secret2 = bitmart_token_production.get_token_boxcapital_prod()
    # bitmart1 = BitMartAuth(bitmart_base_url_production, token1, secret1)
    # bitmart2 = BitMartAuth(bitmart_base_url_production, token2, secret2)
    #
    # order1 = bitmart1.place_order("BTC_USDT", 10, 4141.03, "sell")
    # order2 = bitmart2.place_order("BTC_USDT", 10, 4141.03, "buy")


    # token1 = bitmart_token_production.get_token_yao_prod()
    # token2 = bitmart_token_production.get_token_afund_prod()
    # bitmart1 = BitMartAuth(bitmart_base_url_production, token1)
    # bitmart2 = BitMartAuth(bitmart_base_url_production, token2)

    # order1 = bitmart1.place_order("XLM_USDT", 80000, 0.16063393, "sell")
    # order2 = bitmart2.place_order("XLM_USDT", 80000, 0.16063393, "buy")

    # token1 = bitmart_token_production.get_token_biboxfund_prod()
    # token2 = bitmart_token_production.get_token_yao_prod()
    # bitmart1 = BitMartAuth(bitmart_base_url_production, token1)
    # bitmart2 = BitMartAuth(bitmart_base_url_production, token2)

    # order1 = bitmart1.place_order("OMG_ETH", 1715.23, 0.012867, "sell")
    # order2 = bitmart2.place_order("OMG_ETH", 1715.23, 0.012867, "buy")

    # token1 = bitmart_token_production.get_token_yao_prod()
    # token2 = bitmart_token_production.get_token_afund_prod()
    # bitmart1 = BitMartAuth(bitmart_base_url_production, token1)
    # bitmart2 = BitMartAuth(bitmart_base_url_production, token2)

    # order1 = bitmart1.place_order("XLM_USDT", 80000, 0.16063393, "sell")
    # order2 = bitmart2.place_order("XLM_USDT", 80000, 0.16063393, "buy")


    # time.sleep(1)
    # bitmart1.cancel_order(order1)
    # bitmart2.cancel_order(order2)


    # token = bitmart_token_production.get_token_one_prod()
    # hotfix = BitMartAuth(bitmart_base_url_production, token)
    # hotfix.cancel_all("ONE_ETH", "sell")

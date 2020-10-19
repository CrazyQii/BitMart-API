from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from bitmart.bitmart_auth import BitMartAuth
from gateway.bitmart.bitmart_public import BitMartPublic
from key import bitmart_token_production
from gateway.base_url import bitmart_base_url_production
import random
import time

if __name__ == "__main__":
    bitmart_public = BitMartPublic(bitmart_base_url_production)

    target_orders = 40
    while True:
        try:
            token, secret = bitmart_token_production.get_token_yao_prod()
            hotfix = BitMartAuth(bitmart_base_url_production, token, secret)
            orders_now = hotfix.in_order_list("BTC_USDT")
            print "now we have orders: " + str(len(orders_now))
            ob = bitmart_public.get_orderbook("BTC_USDT")
            asks = ob["sells"]
            
            if len(asks) < target_orders and len(orders_now) < 25:
                ask1_price =float(asks[0]["price"])
                num_new_orders = target_orders - len(asks)
                for i in range(num_new_orders):
                    price = ask1_price + random.randint(10000, 20000) / 100.0
                    num = random.randint(10, 200) / 10000.0
                    hotfix.place_order("BTC_USDT", num, price, "sell")
                    print "new sell order: " + str(price) + ", " + str(num)
                    
            orders_now = hotfix.in_order_list("BTC_USDT")
            if len(orders_now) > 25:
                ranked_orders = sorted(orders_now, key = lambda k: float(k["price"]), reverse = True)
                for i in range(len(ranked_orders) - 25):
                    hotfix.cancel_order(ranked_orders[i]["entrust_id"])
                    
            ask1_price =float(asks[0]["price"])
            orders_now = hotfix.in_order_list("BTC_USDT")
            print "Out of range"
            for o in orders_now:
                if float(o["price"]) > ask1_price + 200.0 or float(o["price"]) < ask1_price + 100.0:
                    hotfix.cancel_order(o["entrust_id"])
                    price = ask1_price + random.randint(10000, 20000) / 100.0
                    num = random.randint(10, 200) / 10000.0
                    hotfix.place_order("BTC_USDT", num, price, "sell")
                    print "new sell order: " + str(price) + ", " + str(num)
                    
        except Exception as e: 
            print e
            continue
            
        try:
            token, secret = bitmart_token_production.get_token_inblockchain_prod()
            hotfix = BitMartAuth(bitmart_base_url_production, token, secret)
            orders_now = hotfix.in_order_list("BTC_USDT")
            print "now we have orders: " + str(len(orders_now))
            ob = bitmart_public.get_orderbook("BTC_USDT")
            bids = ob["buys"]
            
            if len(bids) < target_orders and len(orders_now) < 25:
                bid1_price =float(bids[0]["price"])
                num_new_orders = target_orders - len(bids)
                for i in range(num_new_orders):
                    price = bid1_price - random.randint(10000, 20000) / 100.0
                    num = random.randint(10, 200) / 10000.0
                    hotfix.place_order("BTC_USDT", num, price, "buy")
                    print "new buy order: " + str(price) + ", " + str(num)
                    
            orders_now = hotfix.in_order_list("BTC_USDT")
            if len(orders_now) > 25:
                ranked_orders = sorted(orders_now, key = lambda k: float(k["price"]), reverse = False)
                for i in range(len(ranked_orders) - 25):
                    hotfix.cancel_order(ranked_orders[i]["entrust_id"])
                    
            bid1_price =float(bids[0]["price"])
            orders_now = hotfix.in_order_list("BTC_USDT")
            print "Out of range"
            for o in orders_now:
                if float(o["price"]) < bid1_price - 200.0 or float(o["price"]) > bid1_price - 100.0:
                    hotfix.cancel_order(o["entrust_id"])
                    price = bid1_price - random.randint(10000, 20000) / 100.0
                    num = random.randint(10, 200) / 10000.0
                    hotfix.place_order("BTC_USDT", num, price, "buy")
                    print "new buy order: " + str(price) + ", " + str(num)
                    
        except Exception as e: 
            print e
            continue
                
        print "This loop done!"
        time.sleep(30)
                
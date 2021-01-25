from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from Gateway.bitmart.archived.api_spot import APISpot

class BitmartAuth(object):
    def __init__(self, urlbase, api_key, api_secret, password):
        self.spotAPI = APISpot(api_key, api_secret, password, url=urlbase)

    def place_buy_order(self, symbol, amount, price):
        try:
            result, r = self.spotAPI.post_submit_limit_buy_order(symbol, amount, price)
            order_id = None
            if result["code"] == 1000:
                order_id = result["data"]["order_id"]
            else:
                message = result["message"]
                print("Bitmart auth error: %s" % message)
            return order_id
        except Exception as e:
            print("Bitmart auth place buy order error: %s" % e)
    
    def place_sell_order(self, symbol, amount, price):
        try:
            result, r = self.spotAPI.post_submit_limit_sell_order(symbol, amount, price)
            order_id = None
            if result["code"] == 1000:
                order_id = result["data"]["order_id"]
            else:
                message = result["message"]
                print("Bitmart auth error: %s" % message)
            return order_id
        except Exception as e:
            print("Bitmart auth place sell order error: %s" % e)

    def place_order(self, symbol, amount, price, side):
        try:
            if side == "buy":
                order_id = self.place_buy_order(symbol, str(amount), str(price))
            elif side == "sell":
                order_id = self.place_sell_order(symbol, str(amount), str(price))
            else:
                print("side is wrong")
                return None
            return order_id
        except Exception as e:
            print("Bitmart auth place order error: %s" % e)

    def place_oc_order(self, symbol, amount, price, side):
        try:
            #code: 1000; 50020（余额不足）; 50019（高于盘口）; 50008(低于盘口)
            result, r = self.spotAPI.post_custom_order(symbol, amount, price, side)
            if result["code"] == 1000:
                content = result["data"]
            else:
                content = result["message"]
                print("place oc order %s" % content)
            return result["code"]
        except Exception as e:
            print("Bitmart auth place oc order error: %s" % e)

    def cancel_order(self, symbol, order_id):
        try:
            result, r = self.spotAPI.post_cancel_order(symbol, order_id)
            data = {"data":False}
            message = None
            if result["code"] == 1000:
                data = result["data"]
                message = result["message"]
            else:
                message = result["message"]
        
            info = {
            "func_name": "cancel_order",
            "order_id": order_id,
            "message": message,
            "data": data
            }
            print("Bitmart auth cancel order: %s" % info)
            return info
        except Exception as e:
            print("Bitmart auth cancel order error: %s" % e)

    def cancel_all(self, symbol, side):
        try:
            result, r = self.spotAPI.post_cancel_orders(symbol, side)
            data = {}
            message = None
            if result["code"] == 1000:
                data = result["data"]
                message = result["message"]
            else:
                message = result["message"]
                print("Bitmart auth cancel all error: %s" % message)
            info = {
            "func_name": "cancel_all",
            "message": message,
            "data": data
            }
            return info
        except Exception as e:
            print("Bitmart auth cancel all order error: %s" % e)

    def order_detail(self, symbol, order_id):
        try:
            result, r = self.spotAPI.get_user_order_detail(symbol, order_id)
            order_detail = {}
            if result["code"] == 1000:
                data = result["data"]
                message = result["message"]
                order_detail = {
                    "order_id": data["order_id"],
                    "symbol": data["symbol"],
                    "side": data["side"],
                    "price": data["price"],
                    "amount": data["size"],
                    "price_avg": data["price_avg"],
                    "filled_amount": data["filled_size"],
                    "status": data["status"],
                    "create_time": data["create_time"]
                }
            else:
                message = result["message"]
                print("Bitmart auth order detail error: %s" % message)
            info = {
            "func_name": "order_detail",
            "order_id": order_id,
            "message": message,
            "data": order_detail
            }
            return info
        except Exception as e:
            print("Bitmart auth order detail error: %s" % e)

    def open_orders(self, symbol):
        try:
            orders = []
            for page in [5, 4, 3, 2, 1]:
                orders_on_this_page = self.order_list(symbol, 9, page)
                if orders_on_this_page and len(orders_on_this_page) > 0:
                    orders.extend(orders_on_this_page)
            return orders
        except Exception as e:
            print("Bitmart auth open orders error: %s" % e)

    def order_list(self, symbol, status, page):
        try:
            result, r = self.spotAPI.get_user_orders(symbol, page, 100, status)
            order_list = []
            if result["code"] == 1000:
                orders = result["data"]["orders"]
                for order in reversed(orders):
                    order_list.append({
                        "order_id": order["order_id"],
                        "symbol": order["symbol"],
                        "amount": float(order["size"]),
                        "price": float(order["price"]),
                        "side": order["side"],
                        "price_avg": float(order["price_avg"]),
                        "filled_amount": float(order["filled_size"]),
                        "create_time": order["create_time"]
                    })
            else:
                message = result["message"]
                print("Bitmart auth error: %s" % message)
            return order_list
        except Exception as e:
            print("Bitmart auth order list error: %s" % e)

    def wallet_balance(self):
        try:
            result, r = self.spotAPI.get_wallet()
            balance, frozen = {}, {}
            if result["code"] == 1000:
                wallet = result["data"]["wallet"]
                balance = {row["id"]: row["available"] for row in wallet}
                frozen = {row["id"]: row["frozen"] for row in wallet}
            else:
                message = result["message"]
                print("Bitmart auth error: %s" % message)
            return balance, frozen
        except Exception as e:
            print("Bitmart auth wallet balance error: %s" % e)
            return {}, {}

    def get_trades(self, symbol,offset=1,limit=100):
        try:
            user_trades = []
            result, r = self.spotAPI.get_user_trades(symbol, offset, limit)
            if result["code"] == 1000:
                user_trades.extend(result["data"]["trades"])
            else:
                message = result["message"]
                print("Bitmart auth error: %s" % message)
            return user_trades
        except Exception as e:
            print("Bitmart auth get user trades error: %s" % e)


if __name__ == "__main__":
    api_key = "h218b0bfc374890afa0e88ffa8af06b869e3dca4"
    secret_key = "6c6c98544461bbe71db2bca4c6d7fd0021e0ba9efc215f9c6ad41852df9d9df9"
    password = "123ABC"
    test = BitMartAuth("http://api-cloud.bitmartdev.com", api_key, secret_key, password)
    order = test.place_order("BTC_USDT", 0.1, 9250, "buy")
    # print(order)
    # oc_code = test.place_oc_order("BTC_USDT", 0.01, 9300, "buy")
    # print(oc_code)
    detail = test.order_detail("BTC_USDT", 2147623327)
    test.cancel_all("BTC_USDT", "buy")
    test.cancel_all("BTC_USDT", "sell")
    open_orders = test.open_orders("BTC_USDT")
    for order in open_orders:
        if float(order["price"]) == 0.03:
            c_order = test.cancel_order("BTC_USDT",order["order_id"])
            print(c_order)
    balance, frozen = test.wallet_balance()
    print(balance)
    print(frozen)

from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import datetime
import base64
import hmac
import json
from okex.okex_public import OkexPublic


class OkexAuth(OkexPublic):
    def __init__(self, urlbase, api_key, api_secret, passphrase):
        super().__init__(urlbase)
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
    
    def symbol_convert(self, symbol):
        return '-'.join(symbol.split('_'))
    
    def sign_message(self, data):
        try:
            mac = hmac.new(bytes(self.api_secret, encoding='utf8'), bytes(data, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            return base64.b64encode(d)
        except Exception as e:
            print(e)

    def place_order(self, symbol, amount, price, side):
        try:
            url = self.urlbase + "api/spot/v3/orders"
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                    "type": "limit", 
                    "side": side, 
                    "instrument_id": self.symbol_convert(symbol), 
                    "size": amount, 
                    "price": price
                    }
            message = ts + "POST" + "/api/spot/v3/orders" + json.dumps(params)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }

            is_ok, content = self.request("POST", url, data = json.dumps(params), headers = headers)
            if is_ok:
                return content["order_id"]
            else:
                self.output("place_order", content)
                
        except Exception as e:
            print(e)

    def cancel_order(self, symbol, entrust_id):
        try:
            url = self.urlbase + "api/spot/v3/cancel_orders/%s" % entrust_id
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            params = {
                    "instrument_id": self.symbol_convert(symbol), 
                    "order_id": entrust_id
                    }
            message = ts + "POST" + "/api/spot/v3/cancel_orders/%s" % entrust_id + json.dumps(params)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            is_ok, content = self.request("POST", url, data = json.dumps(params), headers = headers)
            if is_ok:
                info = {
                "func_name": 'cancel_order',
                "entrust_id": entrust_id,
                "response": content
                }
                print(info)
                return is_ok
                
        except Exception as e:
            print(e)

    def order_detail(self, symbol, entrust_id):
        try:
            url = self.urlbase + "api/spot/v3/orders/%s" % entrust_id + "?instrument_id=%s" % self.symbol_convert(symbol)
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/orders/%s" % entrust_id + "?instrument_id=%s" % self.symbol_convert(symbol)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            is_ok, content = self.request("GET", url, headers = headers)
            if is_ok:
                return {"status": content["state"], 
                        "remaining_amount": float(content["size"]) - float(content["filled_size"]), 
                        "timestamp": content["created_at"], 
                        "price": content["price"], 
                        "executed_amount": content["filled_size"], 
                        "symbol": symbol, 
                        "fees": None, 
                        "original_amount": content["size"],  
                        "entrust_id": entrust_id,
                        "side": content["side"]
                        }
            else:
                self.output("order_detail", content)
                
        except Exception as e:
            print(e)

    def open_orders(self, symbol):
        try:
            url = self.urlbase + "api/spot/v3/orders_pending" + "?instrument_id=%s" % self.symbol_convert(symbol)
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/orders_pending" + "?instrument_id=%s" % self.symbol_convert(symbol)
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            
            is_ok, content = self.request("GET", url, headers = headers)
            if is_ok:
                results = []
                for order in content:
                    results.append({
                        "status": order["state"],
                        "remaining_amount": float(order["size"]) - float(order["filled_size"]),
                        "timestamp": order["created_at"],
                        "price": order["price"],
                        "executed_amount": order["filled_size"],
                        "symbol": symbol,
                        "fees": None,
                        "original_amount": order["size"],
                        "entrust_id": order["order_id"],
                        "side": order["side"]
                        })
                return results
                 
            else:
                self.output("in_order_list", content)
                
        except Exception as e:
            print(e)


    def wallet_balance(self):
        try:
            url = self.urlbase + "api/spot/v3/accounts"
            ts = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
            message = ts + "GET" + "/api/spot/v3/accounts"
            signed = self.sign_message(message)
            headers = {"OK-ACCESS-KEY": self.api_key, "OK-ACCESS-SIGN": signed, 
                "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase, 
                "Content-Type": "application/json"
                }
            is_ok, content = self.request("GET", url, headers = headers)
            if is_ok:
                free, frozen = {}, {}
                for currency in content:
                    free[currency["currency"]], frozen[currency["currency"]] = currency["available"], currency["hold"]
                return free, frozen
            else:
                self.output("wallet_balance", content)
                
        except Exception as e:
            print(e)


if __name__ == "__main__":
    okex = OkexAuth("https://www.okex.com/", "", "", "")
    # print(okex.sign_message("123"))
    # print(okex.place_order("XRP_BTC", 30, 0.0002, "sell"))
    # id1 = okex.place_order("XRP_BTC", 15, 0.0001, "sell")
    # id2 = okex.place_order("XRP_BTC", 10, 0.0002, "sell")
    # print(id1)
    # print(okex.order_detail("XRP_BTC", id1))
    # print(okex.open_orders("XRP_BTC"))
    # print(okex.cancel_order("XRP_BTC", id1))
    # print(okex.cancel_order("XRP_BTC", id2))
    print(okex.wallet_balance())

import re
import requests
import json
import urllib
import datetime
import base64
import hashlib
import hmac

TRADE_URL = "https://api.huobi.pro"
TIMEOUT = 5
ACCOUNT_ID = None   # save this without having to query it every time


class HuobiAuth(object):
    def __init__(self, urlbase, api_key, api_secret,password=""):
        self.urlbase = urlbase
        self.api_key = api_key
        self.api_secret = api_secret

    def http_get_request(self, url, params, add_to_headers=None):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = urllib.parse.urlencode(params)
        try:
            response = requests.get(url, postdata, headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "fail"}
        except Exception as e:
            print("httpGet failed, detail is:%s" % e)
            return {"status": "fail", "msg": e}

    def http_post_request(self, url, params, add_to_headers=None):
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json',
            "User-Agent": "Chrome/39.0.2171.71",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = json.dumps(params)
        try:
            response = requests.post(url, postdata, headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                return response.json()
        except Exception as e:
            print("httpPost failed, detail is:%s" % e)
            return {"status": "fail", "msg": e}

    def create_sign(self, pParams, method, host_url, request_path, secret_key):
        sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.parse.urlencode(sorted_params)
        payload = [method, host_url, request_path, encode_params]
        payload = '\n'.join(payload)
        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')
        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature

    def api_key_get(self, params, request_path):
        method = 'GET'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params.update({'AccessKeyId': self.api_key,
                       'SignatureMethod': 'HmacSHA256',
                       'SignatureVersion': '2',
                       'Timestamp': timestamp})
        host_url = TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()

        params['Signature'] = self.create_sign(params, method, host_name, request_path, self.api_secret)
        url = host_url + request_path
        response = self.http_get_request(url, params)
        return response

    def api_key_post(self, params, request_path):
        method = 'POST'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self.api_key,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        host_url = TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.create_sign(params_to_sign, method, host_name, request_path, self.api_secret)
        url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    def symbol_convert(self, symbol):
        try:
            symbol_pair = re.findall("[A-Z]+", symbol)
            symbol_base = symbol_pair[0]
            symbol_quote = symbol_pair[1]
            return (symbol_base + symbol_quote).lower()
        except Exception as e:
            print(e)

    def get_accounts(self):
        # there are three types of accounts: spot, otc, point
        # TODO: choose spot or point
        path = "/v1/account/accounts"
        params = {}
        accounts = self.api_key_get(params, path)["data"]
        try:
            spot_id = [i["id"] for i in accounts if i["type"] == "spot"][0]
        except:
            spot_id = None
        try:
            point_id = [i["id"] for i in accounts if i["type"] == "point"][0]
        except:
            point_id = None
        return spot_id, point_id

    def place_order(self, symbol, amount, price, _type):
        """
        :param amount:
        :param symbol:
        :param _type: buy-market, sell-market, buy-limit, sell-limit
        :param price: price should equal to 0 when using market orders
        """
        try:
            source = "api"  # api, if traded on margin, use 'margin-api'
            try:
                spot_id, point_id = self.get_accounts()
                acct_id = spot_id
                # acct_id = point_id
            except BaseException as e:
                print('get acct_id error.%s' % e)
                acct_id = ACCOUNT_ID

            if _type == "buy":
                _type = "buy-limit"
            elif _type == "sell":
                _type = "sell-limit"

            symbol = self.symbol_convert(symbol)

            params = {"account-id": acct_id,
                    "amount": str(amount),
                    "symbol": symbol,
                    "type": _type,
                    "source": source}
            if price:
                params["price"] = str(price)

            url = '/v1/order/orders/place'
            response = self.api_key_post(params, url)
            return response["data"]
        except Exception as e:
            print(e)

    def open_orders(self, symbol):
        try:
            code = self.symbol_convert(symbol)
            params = {"symbol": code}
            url = "/v1/order/openOrders"
            response = self.api_key_get(params, url)["data"]
            results = []
            if response:
                for order in response:
                    results.append({
                                    "status": order["state"], 
                                    "remaining_amount": float(order["amount"]) - float(order["filled-amount"]), 
                                    "timestamp": order["created-at"], 
                                    "price": order["price"], 
                                    "executed_amount": order["filled-amount"], 
                                    "symbol": symbol, 
                                    "fees": order["filled-fees"], 
                                    "original_amount": order["amount"],  
                                    "entrust_id": order["id"], 
                                    "side": "sell" if order["type"]=="sell-limit" else "buy"
                                    })
                return results
            return results
        except Exception as e:
            print(e)
    def wallet_balance(self):
        try:
            global ACCOUNT_ID
            try:
                spot_id, point_id = self.get_accounts()
            except BaseException as e:
                print('get acct_id error.%s' % e)

            url = "/v1/account/accounts/{0}/balance".format(spot_id)
            params = {"account-id": spot_id}
            balances = self.api_key_get(params, url)["data"]["list"]
            free, frozen = {}, {}
            if balances:
                for balance in balances:
                    if balance["type"] == "trade":
                        free[(balance["currency"]).upper()] = balance["balance"]
                    elif balance["type"] == "frozen":
                        frozen[(balance["currency"]).upper()] = balance["balance"]  
            return free, frozen
        except Exception as e:
            print(e)

    def cancel_order(self, symbol, order_id):
        try:
            params = {}
            url = "/v1/order/orders/{0}/submitcancel".format(order_id)
            return self.api_key_post(params, url)
        except Exception as e:
            print(e)

    def order_detail(self, order_id):
        try:
            params = {}
            url = "/v1/order/orders/{0}".format(order_id)
            return self.api_key_get(params, url)["data"]
        except Exception as e:
            print(e)

if __name__ == "__main__":
    
    huobi = HuobiAuth(TRADE_URL, "27d12a70-dqnh6tvdf3-e76a8755-1bf87", "fe75524c-7b5b13fd-44d6c89b-e9fa9")

    # print(huobi.get_accounts())
    # order = huobi.place_order("htusdt", 1, 5, "sell")
    # print(order)
    # orders = huobi.open_orders("HT_USDT")
    # print(orders)
    # print(huobi.order_info("36946029573"))
    # balance, frozen = huobi.wallet_balance()
    # print(balance["USDT"])
    # print(huobi.cancel_order(47015209016))
    # print(huobi.order_detail("36946029573"))

    # def get_para_str(self, data, requests_method):
    #     try:
    #         timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    #         para_dict = {"AccessKeyId": self.api_key, "SignatureMethod": "HmacSHA256", "SignatureVersion": "2",
    #                      "Timestamp": timestamp}
    #         if requests_method == "GET":
    #             para_dict.update(data)
    #         para_list = []
    #         for key, value in para_dict.items():
    #             para_list.append(str(key) + "=" + str(value))
    #         para_list.sort()
    #         para_str = "&".join(para_list)
    #         return para_str
    #     except Exception as e:
    #         print(e)
    #
    # def sign(self, data, requests_method, request_path):
    #     try:
    #         para_str = self.get_para_str(data, requests_method)
    #         sign_list = [requests_method, urlparse.urlparse(self.urlbase).netloc, request_path, para_str]
    #         sign_str = "\n".join(sign_list)
    #         sign_encode = sign_str.encode(encoding="UTF8")
    #         secret_encode = self.api_secret.encode(encoding="UTF8")
    #
    #         digest = hmac.new(secret_encode, sign_encode, digestmod=hashlib.sha256).digest()
    #         signature = base64.b64encode(digest)
    #         return signature.decode()
    #
    #     except Exception as e:
    #         print(e)
    #
    # def place_order(self, symbol):
    #     try:
    #         symbol = self.symbol_convert(symbol)
    #         headers = {
    #             "Accept": "application/json",
    #             'Content-Type': 'application/json',
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
    #         }
    #
    #
    #     except Exception as e:
    #         print(e)
    #         return None
    #
    # def get_accounts(self):
    #     try:
    #         headers = {
    #             "Content-type": "application/x-www-form-urlencoded",
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
    #         }
    #         url = self.urlbase + "/v1/account/accounts"
    #         data = {}
    #         signature = self.sign(data, "GET", "/v1/account/accounts")
    #         data["signature"] = signature
    #         data = urllib.urlencode(data)
    #         response = requests.get(url, data, headers=headers)
    #         print(response.content)
    #     except Exception as e:
    #         print(e)



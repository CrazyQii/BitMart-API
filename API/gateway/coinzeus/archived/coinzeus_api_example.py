import requests
import json
import time

URL_TOKEN = "https://oauth.coinzeus.io/api/oauth/token"
URL_PREFIX = "https://api2.coinzeus.io"
LOGIN_NAME = "xxx"
PASSWORD = "xxx"
BASIC_KEY = "Y3J5cHRvLWV4Y2hhbmdlLXdlYjo1YzFmZWIyZWUxOWQ4NTcyNzBkNjY1NzVkYjIzMTg0MzlhN2UwZmI0ODAyZTE0MTJhODYzMjc2ZjMwMTQ2ZThj"

class API(object):

    def __init__(self):
        self.expire_t = 0
        self.token = ''

    def request(self, method, path, data=None, headers=None):

        try:
            resp = requests.request(method, path, data=data, headers=headers)

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
    # 
    '''
    @response
        request https://oauth.coinzeus.io/api/oauth/token
        response example:
        {
            u'status':u'0', 
            u'mb_no': 1733, 
            u'access_token': u'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aGVfZmlyc3RfbG9naW4iOiJOIiwibWJfbm8iOjE3MzMsInVzZXJfbmFtZSI6ImpveWRhbmV2ZXJ5QGdtYWlsLmNvbSIsImV4cCI6MTU0OTc0ODM1NSwibWVzc2FnZSI6IlByb2Nlc3NlZC4iLCJtX3Rva2VuIjoiIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9NWV9DTElFTlQiXSwianRpIjoiNTVhYmQ3ZDItYzM3ZC00MDU2LTkwZTMtM2E3MWFiMWZlNGM5IiwiY2xpZW50X2lkIjoiY3J5cHRvLWV4Y2hhbmdlLXdlYiIsInN0YXR1cyI6IjAifQ.Om7e_IKoCeQRQRb_rvWJ-Uet0hidKbPAm9M6AMe3V6avaXfDWkEx6t4N74scZHG9-_itam2RKxIE1rgXnIYtsom_N4_QkfgDdvNlPmtBG6TpMULaDdItaagm8V2sR97NnNUyuGInD4zW-sHtBsMDqVq0umUxvHGyKQGo2NAUSC9WbFG3KYII5wRz6uEhxjYSprrnm3FzawL57nS-eBmbXnHQrXlTRLWGH8UgA-bwMtBsS2E_u1hY-3nIbMUABFqK-Pg_4wnlGNBtoqa7-PpVWvthPH7NkQUQcDAR-793g3PBG9uElFRKJ0kMo6c2tgIPwfdItLV2NGPrALerr5j-Gg',
            u'the_first_login': u'N',
            u'expires_in': 35999, 
            u'token_type': u'bearer', 
            u'm_token': u'', 
            u'jti': u'55abd7d2-c37d-4056-90e3-3a71ab1fe4c9', 
            u'message': u'Processed.', 
            u'refresh_token': u'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aGVfZmlyc3RfbG9naW4iOiJOIiwibWJfbm8iOjE3MzMsInVzZXJfbmFtZSI6ImpveWRhbmV2ZXJ5QGdtYWlsLmNvbSIsImF0aSI6IjU1YWJkN2QyLWMzN2QtNDA1Ni05MGUzLTNhNzFhYjFmZTRjOSIsImV4cCI6MTU1MjMwNDM1NSwibWVzc2FnZSI6IlByb2Nlc3NlZC4iLCJtX3Rva2VuIjoiIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9NWV9DTElFTlQiXSwianRpIjoiMmNiZjU5ZGItMWE3Ny00ZTRjLTg0MWMtZGEzYjk1Mzc5MjQzIiwiY2xpZW50X2lkIjoiY3J5cHRvLWV4Y2hhbmdlLXdlYiIsInN0YXR1cyI6IjAifQ.WKlf-WjeNEJ_yeaI0T1Ua9a5ZxA40FIJwqXqR1DLNBHHheFx5bZ5RMDQ55vBa36We54a2yNCD9V76KJCjqbO--6F8VJzBp449q0zfd4upqYdfi2TexZ-AKrmJUiLh0-0mgRsgWiGx_RCYnTxGXqigFUm6xS8GKWgkmqnDdyHNcTEIZaGDrqu5dwIvG4Uh3mYth97zhzs3ntSMBOsMGc0l8MEPF0fm9XNRFmKY12UKBHhwqeFnUgACkd3wx3v2GrJB3h4OSBDRnJBj2Q3OHd9EIra3wTLVNwfH3T_PJrBvRsMQHjcl0p_f3yv4Iz77bbwu6EGlPqf1RzJSD0Eaj-Nhw'
        }
    '''
    def get_token(self):
        now_t = int(time.time())
        if now_t < self.expire_t:
            return self.token

        auth = "Basic " + BASIC_KEY
        headers = {"Authorization": auth}
        data = {"grant_type": "password",
                "username": LOGIN_NAME,
                "password": PASSWORD,
                "use_auth": "LOGIN"}
        is_ok, response = self.request("POST", URL_TOKEN, headers=headers, data=data)
        if is_ok:
            self.token = response['access_token']
            self.expire_t = now_t + 3600 * 2 # expire time is 36000
            return self.token
        print("Error: get_token() error. response:", response)

    '''
    @response
        request https://api2.coinzeus.io/account/balance
        response example:
        {
            "funcName":"balance",
            "status":"0",
            "message":"Success.",
            "data":
                {
                "total":
                {
                    "BTR":0.0,
                    "MARE":0.0,
                    "KDA":0.0,
                    "EYEAL":0.0,
                    "TMTG":0.0,
                    "WPC":0.0,
                    "ARTS":0.0,
                    "BTC":0.0,
                    ...
                }
            }
        }
    '''
    def get_balance(self):
        token = self.get_token()
        url = URL_PREFIX + "/account/balance"
        if token:
            headers = {"Authorization": "Bearer " + token}
            data = {"mbId": LOGIN_NAME}
            is_ok, response = self.request("POST", url, headers=headers, data=data)
            if is_ok:
                return response['access_token']
            else:
                print("Error: get_balance() error. response:", response)

    '''
    @response
        request https://api2.coinzeus.io/ticker/orderBook
        response example:
        {
          "funcName": "orderBook",
          "status": "0",
          "message": "Success.",
          "data": {
            "tickUnit": "0.0000000100",
            "orderMinUnit": "0.0001000000",
            "amountUnit": "0.0010000000",
            "pairName": "WPC/BTC",
            "volumePower": "24.451451844379207039872240980",
            "buyList": [
              {
                "price": "0.0000167",
                "amount": "13.854"
              },
              {
                "price": "0.00001596",
                "amount": "1000.0"
              },
              {
                "price": "0.00001556",
                "amount": "1000.0"
              }
            ],
            "sellList": [
              {
                "price": "0.00001831",
                "amount": "102.955"
              },
              {
                "price": "0.00002011",
                "amount": "270.418"
              },
              {
                "price": "0.00002531",
                "amount": "360.558"
              }
            ]
          }
        }
    '''
    def get_orderbook(self, symbol):
        token = self.get_token()
        url = URL_PREFIX + "/ticker/orderBook"
        if token:
            headers = {"Authorization": "Bearer " + token}
            data = {"pairName": symbol}
            is_ok, response = self.request("POST", url, headers=headers, data=data)
            if is_ok:
                return response
            else:
                print("Error: get_orderbook() error. response:", response)

    '''
    @response
        request https://api2.coinzeus.io/trade/orderPlace
        response example 1:
        {
            u'status': u'5002',
            u'message': u'Insufficient balance.',
            u'funcName': u'orderPlace'
        }

        response example 2:
        {
            "funcName":"orderPlace",
            "status":"0",
            "message":"Success."
        }
    '''
    # @params
    # action: ask, bid
    def place_order(self, symbol, price, amount, action):
        token = self.get_token()
        url = URL_PREFIX + "/trade/orderPlace"
        if token:
            headers = {"Authorization": "Bearer " + token}
            data = {
                "mbId": LOGIN_NAME,
                "pairName": symbol,
                "action": action,
                "price": price,
                "amount": amount}
            is_ok, response = self.request("POST", url, headers=headers, data=data)
            if is_ok:
                return response
            else:
                print("Error: place_order() error. response:", response)

    '''
    @params
        action: bid, ask
    @response
        request https://api2.coinzeus.io/trade/orderCancel
        response example:
        {
            "funcName":"orderCancel",
            "status":"0",
            "message":"Success."
        }
    '''
    def cancel_order(self, symbol, order_id, action, price):
        token = self.get_token()
        url = URL_PREFIX + "/trade/orderCancel"
        if token:
            headers = {"Authorization": "Bearer " + token}
            data = {
                "mbId": LOGIN_NAME,
                "pairName": symbol,
                "ordNo": order_id,
                "action": action,
                "ordPrice": price}
            is_ok, response = self.request("POST", url, headers=headers, data=data)
            if is_ok:
                return response
            else:
                print("Error: calcel_order() error. response:", response)

    ''' 
    @params
        action: bid, ask, all
    @response
        request https://api2.coinzeus.io/trade/openOrders
        response example:
    {u'status': u'0',
        u'message': u'Success.',
        u'data': {
            u'totalCnt': 1,
            u'list': [
                {
                    u'remainAmount': u'0.018',
                    u'ordPrice': u'0.033',
                    u'ordNo': 19020918826,
                    u'ordAmount': u'0.018',
                    u'pairName': u'ETH/BTC',
                    u'mbId': u'joydanevery@gmail.com',
                    u'action': u'ask',
                    u'ordDt': u'20190209151755'
                }
            ]
        },
        u'funcName': u'openOrders'
    }
    '''
    def open_orders(self, symbol, action = "all", cnt = 200):
        token = self.get_token()
        url = URL_PREFIX + "/account/openOrders"
        if token:
            headers = {"Authorization": "Bearer " + token}
            data = {
                "mbId": LOGIN_NAME,
                "pairName": symbol,
                "action": action,
                "cnt": cnt,
                "skipIdx": 0}
            is_ok, response = self.request("POST", url, headers=headers, data=data)
            if is_ok:
                return response
            else:
                print("Error: open_orders() error. response:", response)


def main():
    api = API()
    # result = api.place_order("ETH/BTC", 0.04, 0.018, 'ask')
    # result = api.open_orders("ETH/BTC")
    # result = api.calcel_order("ETH/BTC", 19021011781, "ask", 0.3)
    # print("result:", result)

if __name__ == '__main__':
    main()
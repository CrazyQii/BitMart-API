import requests
import json
import time

TOKEN_ACCESS_URL = "https://oauth.coinzeus.io/api/oauth/token"

class AccessToken(object):

    def __init__(self, login_name, password, basic_key):
        self.login_name = login_name
        self.password = password
        self.basic_key = "Basic " + basic_key

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
  
    def get_token(self):
        headers = {"Authorization": self.basic_key}
        data = {"grant_type": "password",
                "username": self.login_name,
                "password": self.password,
                "use_auth": "LOGIN"}
        is_ok, response = self.request("POST", TOKEN_ACCESS_URL, headers=headers, data=data)
        if is_ok:
            self.token = response['access_token']
            return self.token
        print ("Error: get_token() error. response:", response)
        
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


def main():
    access_token = AccessToken("", "", "")
    # result = api.place_order("ETH/BTC", 0.04, 0.018, 'ask')
    # result = api.open_orders("ETH/BTC")
    # result = api.calcel_order("ETH/BTC", 19021011781, "ask", 0.3)
    # print("result:", result)

if __name__ == '__main__':
    main()
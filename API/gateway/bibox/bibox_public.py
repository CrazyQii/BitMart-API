import re
import requests

class BiboxPublic(object):
    def __init__(self, urlbase):
        self.urlbase = urlbase

    def get_price(self, symbol):
        try:
            url = self.urlbase + "v1/mdata?cmd=deals&pair=%s&size=1" % (symbol)
            response = requests.get(url)
            # print response.content
            return float(response.json()["result"][0]["price"])

        except Exception as e:
            print(e)
            return None

# if __name__ == "__main__":
#     bibox = BiboxPublic()
#     print bibox.get_price("BIX_BTC")

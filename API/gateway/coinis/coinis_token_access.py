from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import requests
import json
try:
    from urllib.parse import urlencode
except Exception as e:
    from urllib import urlencode


def access_token(urlbase, email, app_id, app_secret):
    try:
        data = {"id": email, "client_id": app_id, "client_secret": app_secret}
        headers = {"Content-type": "application/json"}
        url = urlbase + "oauth/token?" + str(urlencode(data))
        response = requests.post(url, headers=headers)
        # print(response.content)
        return response.json()["data"]["access_token"]
    except Exception as e:
        print(e)

# if __name__ == "__main__":

# print access_token("https://www.coinis.co.kr/api/", "cfo@ebcoin.io", "lqVGJTbcCBBwGUEp1x7gU0c76y2A4QgFcLk7OfNoj06rLKhI5n6tK7rYrVtSp", "Z6azB6ggF2xgvs7RYQllVus95XaDzmDZKNPOFPBy1ubomsZQNJ6U2fCDUUlFi")

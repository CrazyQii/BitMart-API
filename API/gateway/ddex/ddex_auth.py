import requests
import json
import time
import configparser
import web3
from web3.auto import w3
from eth_account.messages import defunct_hash_message as dhm

class DdexAuth(object):
    def __init__(self, address, privateKey):
        self.address = address
        self.privateKey = privateKey

    def getHeaders(self):
        try:
            timestamp = str(int(time.time() * 1000))
            message = "HYDRO-AUTHENTICATION@" + timestamp
            signature = self.signMessage(message)
            hydroAuth = self.address + "#" + message + "#" + signature
            headers = {"content-type": "application/json", "Hydro-Authentication": hydroAuth}
            return headers
        except Exception as e:
            print(e)

    def signMessage(self, message):
        try:
            hashedMessage = dhm(text=message)
            signedMessage = w3.eth.account.signHash(hashedMessage, private_key=self.privateKey)
            signature = w3.toHex(signedMessage.signature)
            return signature
        except Exception as e:
            print(e)

    def signOrder(self, orderId):
        try:
            hashedOrder = dhm(hexstr=orderId)
            signedOrder = w3.eth.account.signHash(hashedOrder, private_key=self.privateKey)
            signature = w3.toHex(signedOrder.signature)
            return signature
        except Exception as e:
            print(e)

    def buildOrder(self, symbol, amount, price, side):
        try:
            url = "https://api.ddex.io/v2/orders/build"
            headers = self.getHeaders()
            data = {"amount": amount, "price": price, "side": side, "marketId": symbol}
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            # print("Build order:")
            # print(response.content)
            order = json.loads(response.content)
            orderId = order["data"]["order"]["id"]
            # print(orderId)
            return orderId
        except Exception as e:
            print(e)

    def placeOrder(self, symbol, amount, price, side):
        try:
            url = "https://api.ddex.io/v2/orders"
            headers = self.getHeaders()
            orderId = self.buildOrder(symbol, amount, price, side)
            signature = self.signOrder(orderId)
            data = {"orderId": orderId, "signature": signature}
            data = json.dumps(data)
            response = requests.post(url, data=data, headers=headers)
            # print(response.content)
            return(response.json()["data"]["order"])
        except Exception as e:
            print(e)

    def cancelOrder(self, orderId):
        try:
            url = "https://api.ddex.io/v2/orders/%s" % orderId
            headers = self.getHeaders()
            response = requests.delete(url, headers=headers)
            print(response.content)
        except Exception as e:
            print(e)

    def orderDetail(self, orderId):
        try:
            url = "https://api.ddex.io/v2/orders/%s" % orderId
            headers = self.getHeaders()
            response = requests.get(url, headers=headers)
            # print(response.content)
            return response.json()["data"]["order"]
        except Exception as e:
            print(e)

    def orderList(self, symbol):
        try:
            url = "https://api.ddex.io/v2/orders"
            headers = self.getHeaders()
            data = {"marketId": symbol, "status": "pending", "page": 1, "perPage": 100}
            data = json.dumps(data)
            response = requests.get(url, data=data, headers=headers)
            # print(response.content)
            return response.json()["data"]["orders"]
        except Exception as e:
            print(e)

    def tradeList(self, symbol):
        try:
            url = "https://api.ddex.io/v2/markets/%s/trades/mine" % symbol
            headers = self.getHeaders()
            response = requests.get(url, headers=headers)
            # print(response.content)
            return response.json()
        except Exception as e:
            print(e)

    def getLockedBalance(self):
        try:
            url = "https://api.ddex.io/v2/account/lockedBalances"
            headers = self.getHeaders()
            response = requests.get(url, headers=headers)
            print(response.content)
            return response.json()
        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    # address = "0xA2d6136c13B7afd46f335FfA886Dcae075300BBE".lower()
    # privateKey = "be438d091e48107f4d4740c373cf6d2e70270e53e7765f80b9bed60629a91a3b"

    # address = "0xeE089F1D787116D7633a459fD8b582cCCAdEfADe".lower()
    # privateKey = "9d7402c720e2e9fad33b659121ebf8df32c7e4f4d600c4c76e71be4f9c6c56e4"

    # ddexAuth = DdexAuth(address, privateKey)
    # a = ddexAuth.getHeaders()
    # print(a)
    # ddexAuth.getLockedBalance()
    # a = ddexAuth.placeOrder("BMX-ETH", 100, 0.0001100, "sell")
    # print(a)
    # ddexAuth.orderList("ZRX-ETH")
    # ddexAuth.orderDetail("0x7c832b27e78c258da6e2b10bac936326aabefc0dea018462306d272e41ff537b")
    # ddexAuth.cancelOrder("0x7c832b27e78c258da6e2b10bac936326aabefc0dea018462306d272e41ff537b")




    # print(address)
    # timestamp = str(int(time.time() * 1000))
    # print(timestamp)
    # ddexPublic = DdexPublic()
    # a = ddexPublic.getOrderBook("ZRX-ETH")
    # print(a)

import os
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from restful import UbiexSDK

def main():
    # sdk = UbiexSDK("3ca33abe-e99e-4820-befa-4b24ae370e18", "8b89ac95b6e261d2f53a0803d15cc5941588a322")
    sdk = UbiexSDK("", "")

    # print("balance: ", sdk.getBalance())
    # print("market config: ", sdk.getMarketConfig())
    # print("funds: ", sdk.getFunds())
    print("getDepth: ", sdk.getDepth("btc_usdt"))
    print("getTicker: ", sdk.getTicker("btc_usdt"))
    print("getKline: ", sdk.getKLine("btc_usdt"))



if __name__ == '__main__':
    main()
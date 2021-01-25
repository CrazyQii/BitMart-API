from os import sys, path
import importlib
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import Gateway.base_url as base_url

class IntegratedExchange(object):
    def __init__(self):
        #self.cmc_public = CmcPublic(cmc_base_url)
        pass

    def get_exchange_public(self, market_exchange):
        try:
            exchange_public = None
            cap_name = market_exchange.capitalize()
            lower_name = market_exchange.lower()
            lower_kw =  "public"
            cap_kw = "Public"

            module_path = f"gateway.{lower_name}.{lower_name}_{lower_kw}"
            exchange_module = importlib.import_module(module_path)
            api = getattr(exchange_module,f"{cap_name}{cap_kw}")
            
            url_name = f"{lower_name}_base_url"
            if lower_name == "bitmart":
                url_name += "_production"
            
            url = getattr(base_url, url_name)
            exchange_public = api(url)
            return exchange_public
            
        except Exception as e:
            error_msg = "Integrated Exchange get exchange public error:%s %s" % (e, type(e))
            print(error_msg)


    def get_exchange_auth(self,api_key,secret_key,password,market_exchange):
        try:
            exchange_auth = None
            cap_name = market_exchange.capitalize()
            lower_name = market_exchange.lower()
            lower_kw =  "auth"
            cap_kw = "Auth"

            module_path = f"gateway.{lower_name}.{lower_name}_{lower_kw}"
            exchange_module = importlib.import_module(module_path)
            api = getattr(exchange_module,f"{cap_name}{cap_kw}")
            
            url_name = f"{lower_name}_base_url"
            if lower_name == "bitmart":
                url_name += "_production"
            
            url = getattr(base_url, url_name)
            exchange_auth = api(url,api_key,secret_key,password)
            return exchange_auth

        except Exception as e:
            error_msg = "Integrated Exchange get exchange auth error:%s %s" % (e, type(e))
            print(error_msg)


if __name__ == "__main__":
    integrated = IntegratedExchange()
    for exchange in ["okex","binance","huobi","bitmart"]:
        ak,sk,pwd = ("",)*3
        exchange_auth = integrated.get_exchange_auth(ak,sk,pwd,exchange)
        print(type(exchange_auth))
        exchange_public = integrated.get_exchange_public(exchange)
        print(type(exchange_public))
        print("-"*80)

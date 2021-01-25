"""
Uniswap exchange
API doc: https://thegraph.com/docs/graphql-api#queries
query example: https://thegraph.com/explorer/subgraph/uniswap/uniswap-v2?query=Example%20query
"""

from decimal import Decimal
import requests
import json
import os

cur_path = os.path.abspath(os.path.dirname(__file__))


class UniswapPulib(object):
    def __init__(self):
        self.base_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
        self._get_pairs_address()

    def get_price(self, symbol: str) -> Decimal:
        symbol = self._symbol_convert(symbol)
        price = 0.0
        try:
            with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                data = json.load(f)
            symbol1 = f"{symbol.split('_')[1]}_{symbol.split('_')[0]}"
            # check symbol in json (USDC_ETH or ETH_USDC)
            if symbol in data:  # token_WETH
                address = data[symbol]['id']
                tokenPrice = 'token1Price'  # get the former token price
            elif symbol1 in data:  # WETH_token
                address = data[symbol1]['id']
                tokenPrice = 'token0Price'
            else:
                raise KeyError
            params = {
                'query': '{ pair(id: "' + address + '") { ' + tokenPrice + ' } }'
            }
            result = self._request(params)
            if 'errors' in result:
                raise Exception(result['errors'])
            price = result['data']['pair'][tokenPrice]
        except KeyError:
            print(f'Get price error: Do not have {symbol} symbol in Json')
        except Exception as e:
            print(f'Get price error: {e}')
        finally:
            return self._decimal(price)

    def get_kline(self, symbol: str, time_period: int = 36000) -> list:
        symbol = self._symbol_convert(symbol)
        klines = []
        try:
            with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                data = json.load(f)
            symbol1 = f"{symbol.split('_')[1]}_{symbol.split('_')[0]}"
            if symbol in data:  # token_WETH
                address = data[symbol]['id']
                tokenPrice = 'token1Price'
                volumeToken = 'hourlyVolumeToken1'
            elif symbol1 in data:  # WETH_token
                address = data[symbol1]['id']
                tokenPrice = 'token0Price'
                volumeToken = 'hourlyVolumeToken0'
            else:
                raise KeyError(f'Do not have {symbol} symbol in Json')

            # ---query for hour volume---
            limit = int(time_period / 3600) + 2  # 由于后面需要计算前一天的收盘价作为当天的开盘价，所以多加两天
            params = {
                'query': '{ pairHourDatas(first: ' + str(limit) + ', orderBy: hourStartUnix, orderDirection: desc, '
                'where: {pair: "' + address + '"}) '
                '{ hourStartUnix ' + volumeToken + ' } }'
            }
            result = self._request(params)
            if 'errors' in result:
                raise Exception(result['errors'])
            pairs = result['data']['pairHourDatas']

            # ----query for pair block number in the block chain---
            result = self._get_eth_blocks(pairs)
            if 'errors' in result:
                raise Exception(result['errors'])
            blocks = result['data']

            # ---query for price---
            query_string = ""
            for block in blocks.items():
                query_string += block[0] + ': pair(id: "' + address + '", block:{number: ' \
                                + block[1][0]['number'] + '}) { ' + tokenPrice + ' } '
            params = {
                'query': '{ ' + query_string + ' }'
            }
            result = self._request(params)
            if 'errors' in result:
                raise Exception(result['errors'])
            pair_price = result['data']

            # ---combine price and volume for hours kline---
            for i in range(2, len(pairs)):
                ts_new = 't' + str(pairs[i - 1]['hourStartUnix'])
                ts_old = 't' + str(pairs[i]['hourStartUnix'])
                klines.append({
                    'timestamp': pairs[i]['hourStartUnix'],
                    'open': self._decimal(pair_price[ts_old][tokenPrice]),
                    'high': None,
                    'low': None,
                    'volume': self._decimal(pairs[i][volumeToken]),
                    'last_price': self._decimal(pair_price[ts_new][tokenPrice])
                })
        except KeyError as e:
            print(f'Get kline error: {e}')
        except Exception as e:
            print(f'Get kline error: {e}')
        finally:
            return klines

    def get_trades(self, symbol: str, limit: int = 100) -> list:
        symbol = self._symbol_convert(symbol)
        trades = []
        try:
            with open(f'{cur_path}/symbols_detail.json', 'r') as f:
                data = json.load(f)
            symbol1 = f"{symbol.split('_')[1]}_{symbol.split('_')[0]}"
            if symbol in data:  # token_WETH(standard in uniswap)
                address = data[symbol]['id']
                amount0In = 'amount0In'
                amount1In = 'amount1In'
                amount0Out = 'amount0Out'
                amount1Out = 'amount1Out'
            elif symbol1 in data:  # WETH_token
                address = data[symbol1]['id']
                amount1In = 'amount0In'
                amount0In = 'amount1In'
                amount1Out = 'amount0Out'
                amount0Out = 'amount1Out'
            else:
                raise KeyError(f'Do not have {symbol} symbol in Json')
            params = {
                'query': '{ swaps(first: ' + str(limit) + ', orderBy: timestamp orderDirection: desc, '
                'where: {pair_in: ["' + address + '"]}) { pair { token0 { symbol } token1 { symbol } }'
                ' timestamp amount0In amount1In amount0Out amount1Out } }'
            }
            result = self._request(params)
            if 'errors' in result:
                raise Exception(result['errors'])
            for trade in result['data']['swaps']:
                trades.insert(0, {
                    'amount': self._decimal(trade[amount1Out]) if trade[amount0In] != '0' else self._decimal(trade[amount1In]),
                    'order_time': trade['timestamp'],
                    'price': self._decimal(float(trade[amount1Out]) / float(trade[amount0In]))
                    if trade[amount0In] != '0' else self._decimal(float(trade[amount1In]) / float(trade[amount0Out])),
                    'count': self._decimal(trade[amount0In]) if trade[amount0In] != '0' else self._decimal(trade[amount0Out]),
                    'type': 'buy' if trade[amount0In] != '0' else 'sell'
                })
        except KeyError as e:
            print(f'Get trade error: {e}')
        except Exception as e:
            print(f'Get trade error：{e}')
        finally:
            return trades

    def get_orderbook(self, symbol: str):
        pass

    def _get_pairs_address(self, nums=200) -> None:
        """ get most volume 200 tokens from exchange"""
        try:
            params = {
                'query': '{ pairs(first: ' + str(nums) + ', orderBy: volumeUSD, orderDirection: desc) '
                                                         '{ id token0 { id symbol } token1 { id symbol } } }'
            }
            result = self._request(params)
            data = {}
            for pair in result['data']['pairs']:
                data.update({
                    f"{pair['token0']['symbol']}_{pair['token1']['symbol']}": {
                        'id': pair['id'],
                        f"{pair['token0']['symbol']}": pair['token0']['id'],
                        f"{pair['token1']['symbol']}": pair['token1']['id']
                    }
                })
            # write address(id) into json file
            with open(f'{cur_path}/symbols_detail.json', 'w+') as f:
                json.dump(data, f, indent=1)
        except Exception as e:
            print(f'Get token address error: {e}')

    def _get_eth_blocks(self, pairs: list) -> dict:
        """
        get block number from ethereum
        """
        try:
            url = 'https://api.thegraph.com/subgraphs/name/blocklytics/ethereum-blocks'
            # pairs
            query = ''
            for i in range(0, len(pairs) - 1):
                query += 't' + str(pairs[i + 1]['hourStartUnix']) + \
                         ': blocks(first: 1, orderBy: timestamp, orderDirection: desc, where: {timestamp_gt: ' \
                         + str(pairs[i + 1]['hourStartUnix']) + ', timestamp_lt: ' \
                         + str(pairs[i + 1]['hourStartUnix'] + 600) + '}) {number, timestamp} '
            params = {
                'query': '{' + query + '}'
            }
            resp = requests.post(url, data=json.dumps(params))
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f'request error: {resp.status_code}')
                return resp.json()
        except Exception as e:
            print(f'Get eth blocks error: {e}')
            return {'errors': e}

    # ----------utils-----------

    def _request(self, params: dict) -> dict:
        try:
            resp = requests.post(self.base_url, data=json.dumps(params))
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f'request error: {resp.status_code}')
                return resp.json()
        except Exception as e:
            print(f'Network error: {e}')
            return {'errors': e}

    def _symbol_convert(self, symbol: str):
        # ETH and BTC must be replaced by WETH and WBTC in Uniswap
        return symbol.replace('ETH', 'WETH').replace('BTC', 'WBTC')

    def _decimal(self, number):
        try:
            return Decimal(number).quantize(Decimal('0.0000'))
        except Exception as e:
            print(f'convert flaot number error: {e}')


if __name__ == '__main__':
    u = UniswapPulib()
    # ETH_USDC 和 USDC_ETH 价格相对应
    # print(u.get_price('ETH_USDC'))
    # print(u.get_trades('ETH_USDC'))
    # print(u.get_kline('ETH_USDC'))

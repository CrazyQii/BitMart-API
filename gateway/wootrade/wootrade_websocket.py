from threading import Thread
import websocket
import json
import time


class WootradeWs(Thread):
    def __init__(self, urlbase, application_id):
        super().__init__()
        self.urlbase = urlbase
        self.application_id = application_id
        self.data = {}

    def _symbol_convert(self, symbol: str):
        return 'SPOT_' + symbol

    def _connect_auth(self, symbol: str = None):
        # connect authentication endpoint
        ws = None
        symbol = self._symbol_convert(symbol)
        sub_url = f'{self.urlbase}{self.application_id}/{symbol}'
        while True:
            try:
                time.sleep(2)
                print(f'start to connect auth {sub_url}')
                ws = websocket.create_connection(sub_url)
                break
            except Exception as e:
                print(f'Wootrade connect auth error {e}')
                continue
        return ws

    def _connect_public(self, streams=None):
        # connect public endpoint
        if streams is None:
            streams = ['ticker', 'bbo']
        ws = None
        sub_url = f'{self.urlbase}stream?streams={",".join(streams)}'
        while True:
            try:
                time.sleep(2)
                print(f'start to connect public {sub_url}')
                ws = websocket.create_connection(sub_url)
                break
            except Exception as e:
                print(f'Wootrade connect public error {e}')
                continue
        return ws

    def _get_orderbook(self, data: dict):
        orderbook = {'buys': [], 'sells': []}
        total_amount_buys = 0
        total_amount_sells = 0
        for item in data['data']['bids']:
            total_amount_buys += float(item['quantity'])
            orderbook['buys'].append({
                'amount': float(item['quantity']),
                'total': total_amount_buys,
                'price': float(item['price']),
                'count': 1
            })
        for item in data['data']['asks']:
            total_amount_sells += float(item['quantity'])
            orderbook['sells'].append({
                'amount': float(item['quantity']),
                'total': total_amount_sells,
                'price': float(item['price']),
                'count': 1
            })
        return orderbook

    def _get_trade(self, data: dict):
        try:
            trade = data['data']
            trade = {
                'amount': float(trade['quantity']) * float(trade['price']),
                'order_time': round(data['timestamp'] / 1000),
                'price': float(trade['price']),
                'count': float(trade['quantity']),
                'type': trade['side'].lower()
            }
            return trade
        except Exception as e:
            print(e)

    def _update_order(self, data: dict):
        try:
            order = data['data']
            order = {
                'order_id': order['order_id'],
                'symbol': order['symbol'],
                'side': order['side'].lower(),
                'price': float(order['order_price']),
                'amount': float(order['order_quantity']),
                'price_avg': None,
                'filled_amount': float(order['executed_quantity']),
                'status': order['status'],
                'create_time': round(data['timestamp'] / 1000)
            }
            return order
        except Exception as e:
            print(e)

    def _get_position(self, data: dict):
        try:
            return data['data']
        except Exception as e:
            print(e)

    def _get_price(self, symbol: str, data: dict):
        try:
            for ticker in data['data']:
                if self._symbol_convert(symbol) == ticker['symbol']:
                    return {
                        'symbol': symbol,
                        'open': ticker['o'],
                        'close': ticker['c']
                    }
        except Exception as e:
            print(e)

    def sub_public(self, symbol: str):
        # Support types
        # ticker / bbo(best bid offer)
        def _public():
            try:
                ws = self._connect_public()
                while True:
                    recv = json.loads(ws.recv())
                    if 'error' in recv and recv['error']:
                        # identify error in receive
                        print(f'Sub event error: {recv["data"]}')
                        break
                    elif recv['event'] == 'ticker':
                        price = self._get_price(symbol, recv)
                        self.data.update({'price': price})
                    elif recv['event'] == 'PING':  # receive ping from server and send pong
                        print(recv)
                        ws.send(json.dumps({'event': 'PONG'}))
                    else:
                        print(recv)
            except websocket.WebSocketException as e:
                print(f'Sub public error {e} : try to connect again')
                _public()
            except Exception as e:
                print(f'Sub public error {e}: connection end')
        Thread(target=_public).start()

    def sub_event(self, symbol: str):
        # Support types
        # book / trade / order_update / position
        def _event():
            try:
                ws = self._connect_auth(symbol)
                while True:
                    recv = json.loads(ws.recv())
                    if 'error' in recv and recv['error']:
                        # identify error in receive
                        print(f'Sub event error: {recv["data"]}')
                        break
                    elif recv['event'] == 'TRADE':
                        trade = self._get_trade(recv)
                        self.data.update({'trade': trade})
                    elif recv['event'] == 'BOOK':
                        orderbook = self._get_orderbook(recv)
                        self.data.update({'orderbook': orderbook})
                    elif recv['event'] == 'ORDER_UPDATE':
                        order = self._update_order(recv)
                        self.data.update({'order': order})
                    elif recv['event'] == 'POSITIONS':
                        position = self._get_position(recv)
                        self.data.update({'position': position})
                    elif recv['event'] == 'PING':  # receive ping from server and send pong
                        print(recv)
                        ws.send(json.dumps({'event': 'PONG'}))
                    else:
                        print(recv)
            except websocket.WebSocketException as e:
                print(f'Sub event error {e} : try to connect again')
                _event()
            except Exception as e:
                print(f'Sub event error {e}: connection end')
        Thread(target=_event).start()

    def sub_price(self, symbol: str):
        self.sub_public(symbol)

    def sub_bbo(self, symbol: str):
        # best bid offer
        self.sub_public(symbol)

    def sub_orderbook(self, symbol: str):
        self.sub_event(symbol)

    def sub_kline(self, symbol: str):
        pass

    def sub_order(self, symbol: str):
        self.sub_event(symbol)

    def sub_trade(self, symbol: str):
        self.sub_event(symbol)

    def sub_position(self, symbol: str):
        self.sub_event(symbol)


if __name__ == '__main__':
    woo = WootradeWs('wss://api.woo.network/ws/', 'e1f40bde-0e4e-4c2c-b369-bd00e434b754')
    # woo.sub_price('BTC_USDT')
    woo.sub_trade('BTC_USDT')

    # while True:
    #     time.sleep(3)
        # print(woo.data['price'])
        # print(woo.data['bbo'])
        # print(woo.data['trade'])
        # print(woo.data['orderbook'])
        # print(woo.data['order'])
        # print(woo.data['position'])

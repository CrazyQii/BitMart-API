from bs4 import BeautifulSoup
from all_symbols import mm_symbols, ty_symbols
import requests
import pandas as pd
import time


class BitmartCrawling(object):
    def __init__(self):
        self.base_url = 'https://www.coingecko.com/zh/exchanges/bitmart'  # 前100条
        self.base_url_more = 'https://www.coingecko.com/zh/exchanges/bitmart/show_more_tickers?page=1&per_page=100&verified_ticker=true&ticker_type=undefined'  # 后100条
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }
        self.init_csv()

    def symbol_convert(self, symbol: str):
        return symbol.replace('/', '_')

    def init_csv(self):
        """ 写入文件头 """
        try:
            a = pd.DataFrame(columns=['symbol', 'price', 'spread', 'depth+2%', 'depth-2%', 'volume', 'volume%', 'spread>5%', 'category'])
            a.to_csv('data.csv', mode='w', index=False)
            print('Init csv file successfully!')
        except Exception as e:
            print(f'Init csv error:{e}')

    def write_to_csv(self, data):
        """ 写入文件 """
        try:
            data = pd.DataFrame(data)
            data.to_csv('data.csv', mode='a', index=False, header=False)
        except Exception as e:
            print(f'Write to csv error:{e}')

    def request_page(self, url, more=False):
        try:
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                # 前100条和后100条页面结构不同，所以分开解析
                self.parse_page(resp, more)
            else:
                print(f'request error, status code：{resp.status_code}')
        except Exception as e:
            print(f'Network error:{e}')
            print('Start to request 2s later...')
            time.sleep(2)
            self.request_page(url, more)

    def parse_page(self, content, more):
        """ 解析前100条页面 """
        try:
            soup = BeautifulSoup(content.content.decode('utf-8'), 'lxml')
            if soup is None:
                print(f'{"-"*10}数据为空{"-"*10}')
                return
            # 判断是加载前100页还是100页以后
            if more is not True:
                tickers = soup.find('tbody', attrs={'data-target': 'exchanges.tablebody'}).find_all('tr')
            else:
                tickers = soup.find_all('tr')
            # 解析对应的条目
            for ticker in tickers:
                symbol = ticker.find_all('td')[3].find('a').get_text().replace('\n', '')
                price = ticker.find_all('td')[4].find('div').get_text().replace('\n', '')
                spread = ticker.find_all('td')[5].get_text().replace('\n', '')
                # 处理 spread>5% 分类
                if spread == '-' or float(spread.split('%')[0]) > 5:
                    limit_spread = 1
                else:
                    limit_spread = 0

                # 处理 symbol 分类
                if self.symbol_convert(symbol) in mm_symbols:
                    category = 1
                elif self.symbol_convert(symbol) in ty_symbols:
                    category = 2
                elif limit_spread == 0:
                    category = 3
                else:
                    category = 4

                info = {
                    'symbol':  symbol,
                    'price':  price,
                    'spread':  spread,
                    'depth+2%':  ticker.find_all('td')[6].get_text().replace('\n', ''),
                    'depth-2%':  ticker.find_all('td')[7].get_text().replace('\n', ''),
                    'volume':  ticker.find_all('td')[8].find('div').get_text().replace('\n', ''),
                    'volume%':  ticker.find_all('td')[9].get_text().replace('\n', ''),
                    'spread>5%': limit_spread,
                    'category': category
                }
                print(info)
                self.write_to_csv([info])
            print(f'{"-"*10}{len(tickers)} items were wrote into csv {"-"*10}')
        except Exception as e:
            print(f'Parse page error:{e}')

    def run(self):
        try:
            self.request_page(self.base_url)
            self.request_page(self.base_url_more, more=True)
            print(f'{"-"*10}Function end{"-"*10}')
        except Exception as e:
            print(f'Main function error: {e}')


if __name__ == '__main__':
    b = BitmartCrawling()
    b.run()

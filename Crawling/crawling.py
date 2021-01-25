from bs4 import BeautifulSoup
from all_symbols import mm_symbols, ty_symbols
from auto_email import AutoEmail
from openpyxl import Workbook
import requests
import time


class BitmartCrawling(object):
    def __init__(self):
        self.base_url = 'https://www.coingecko.com/zh/exchanges/bitmart'  # 前100条
        self.base_url_more = 'https://www.coingecko.com/zh/exchanges/bitmart/show_more_tickers?page=1&per_page=100&verified_ticker=true&ticker_type=undefined'  # 后100条
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }
        self.data = []

    def symbol_convert(self, symbol: str):
        return symbol.replace('/', '_')

    def write_to_xlsx(self):
        """ 写入数据到excel """
        try:
            wb = Workbook()  # 创建工作簿
            ws = wb.active  # 正在运行的工作表
            ws.title = 'data'  # 表名称
            header = ['symbol', 'price', 'spread', 'depth+2%', 'depth-2%', 'volume', 'volume%', 'spread>5%', 'category']
            ws.append(header)  # 添加索引
            for row, item in enumerate(self.data):  # 添加数据
                ws.append(item)
            wb.save('data.xlsx')
            print('Save data to excel successfully!')
        except Exception as e:
            print(f'Write to xlsx error: {e}')

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

                info = [
                    symbol,
                    price,
                    spread,
                    ticker.find_all('td')[6].get_text().replace('\n', ''),  # depth+2%
                    ticker.find_all('td')[7].get_text().replace('\n', ''),  # depth-2%
                    ticker.find_all('td')[8].find('div').get_text().replace('\n', ''),  # volume
                    ticker.find_all('td')[9].get_text().replace('\n', ''),  # volume%
                    limit_spread,  # spread>5%
                    category  # category
                ]
                print(info)
                self.data.append(info)
            print(f'{"-"*10}{len(tickers)} items were wrote into csv {"-"*10}')
        except Exception as e:
            print(f'Parse page error:{e}')

    def run(self):
        try:
            print(f'{"-"*10}Start to crawl{"-"*10}')
            self.request_page(self.base_url)
            self.request_page(self.base_url_more, more=True)
            self.write_to_xlsx()  # 写入数据
            print('Send email after 5s!')
            time.sleep(5)
            # 发送信息
            email = AutoEmail()
            email.send()
            print(f'{"-"*10}Function end{"-"*10}')
        except Exception as e:
            print(f'Main function error: {e}')


if __name__ == '__main__':
    b = BitmartCrawling()
    b.run()
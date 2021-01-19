from ExchangeCenter.client import client
import pandas as pd
from pyecharts.charts import *
from pyecharts import options as opts
from pyecharts.globals import CurrentConfig
import numpy as np
from sklearn.neighbors import KernelDensity
import logging

CurrentConfig.ONLINE_HOST = "https://cdn.kesci.com/lib/pyecharts_assets/"


class WssPredict(object):
    """ websocket 连续获取数据 """
    def __init__(self):
        self.order = []

    def _max_profit(self, x_data: list, y_data: list, rate: float):
        """
        最大利润
        @param x_data: 价格
        @param y_data: 价格出现概率
        @param rate: 手续费率
        @return 利润概率，最小买入价下标，最大卖出价下标，最小买入价，最大卖出价
        """
        max_pro = 0  # 最大利润
        min_buy_i = 0  # 最小买单价下标
        max_sell_i = 0  # 最大卖单价下标
        min_sell_i = 0  # 最小卖单价下标
        for buy_i in range(0, len(x_data)):  # 遍历买单价格
            for sell_i in range(buy_i, len(x_data)):  # 根据费率计算找到有利润的最小卖单价下标
                if x_data[sell_i] - x_data[buy_i] - 2 * rate > 0:
                    min_sell_i = sell_i
                    break
            if min_sell_i == 0:  # 最小卖单价下标为0，说明全局不存在有利润的卖价，结束遍历
                return 0, 0, 0, 0, 0
            for sell_i in range(min_sell_i, len(x_data)):  # 从最小卖单价开始遍历，查找最大利润的最大卖单价下标
                if y_data[sell_i] >= y_data[buy_i]:  # 可卖出数量大于买入数量
                    pro = (x_data[sell_i] - x_data[buy_i]) * (y_data[buy_i])  # 计算利润
                    if pro >= max_pro:  # 标记最大利润，最小买单下标，最大卖单下标
                        max_pro = pro
                        min_buy_i = buy_i
                        max_sell_i = sell_i
        return round(max_pro, 4), min_buy_i, max_sell_i, x_data[min_buy_i], x_data[max_sell_i]

    def display_data(self):
        try:
            # 绘制价格直方图
            for data in client.receiver("PAX_USDT", 'kline', 'binance'):
                dataset = pd.DataFrame(data=data['data'])
                self.show_fig(dataset)
                self.operate(dataset)
                # print(dataset)
        except Exception as e:
            print(f'处理数据函数错误: {e}')

    def show_fig(self, dataset):
        try:
            """ 处理数据，图表展示 """
            data = dataset['last_price'].value_counts(normalize=True).sort_index()
            x_data = list(data.index)
            y_data = list((data.values * 100).round(decimals=2))
            pro, buy_i, sell_i, buy, sell = self._max_profit(x_data, y_data, 0.0001)
            bar = (
                Bar()
                .add_xaxis(x_data)
                .add_yaxis('价格出现概率占比', y_data)
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True)),  # 显示X轴分割线
                    yaxis_opts=opts.AxisOpts(name='概率/%', splitline_opts=opts.SplitLineOpts(is_show=True)),  # 显示Y轴分割线
                    title_opts=opts.TitleOpts(title=f"best_buy: {buy}\n\nbest_sell: {sell}\n\nprofit: {pro}",
                                              pos_right='10%', pos_top='10%')  # 显示标题
                )
                .set_series_opts(
                    label_opts=opts.LabelOpts(is_show=False),
                    markarea_opts=opts.MarkAreaOpts(
                        data=[
                            opts.MarkAreaItem(name="", x=(str(buy), str(sell)), y=('0', str(y_data[buy_i]))),
                        ]))
            )
            bar.render()
        except Exception as e:
            print(f'图表错误函数：{e}')

    def operate(self, dataset):
        data = dataset['last_price'].value_counts(normalize=True).sort_index()  # 计算
        x_data = list(data.index)
        y_data = list((data.values * 100).round(decimals=2))
        logging.basicConfig(filename='predict.log', level=logging.WARNING)
        pro, buy_i, sell_i, buy, sell = self._max_profit(x_data, y_data, 0.0)
        print(dataset.loc[0]['last_price'])
        if dataset.loc[0, 'last_price'] == buy and len(self.order) == 0:  # 买单
            self.order.append(dataset.loc[0])
            logging.error(f'买入:{dataset.loc[0]}')
        if dataset.loc[0, 'last_price'] == sell and len(self.order) == 1:  # 卖单
            self.order.pop()
            logging.error(f'卖出:{dataset.loc[0]}')




class RestPredict(object):
    def show(self):
        dataset = pd.read_csv('BUSD_USDT.csv')
        data = dataset['last_price'].value_counts(normalize=True).sort_index()
        x_data = data.index[:, np.newaxis]
        y_data = (data.values * 100).round(decimals=3)[:, np.newaxis]
        print(y_data)
        # xs = np.linspace(x_data.min(), x_data.max(), 100)[:, np.newaxis]  # 划分x轴
        kde = KernelDensity(kernel='gaussian', bandwidth=0.75).fit(y_data)
        log_density = kde.score_samples(x_data)
        y_data = np.exp(log_density) * 1000 - 260
        print(y_data)
        # # # 处理数据
        # # data = dataset['last_price'].value_counts(normalize=True).sort_index()
        # x_data = list(data.index)
        # # y_data = list((data.values * 100).round(decimals=2))
        # # pro, buy_i, sell_i, buy, sell = self._max_profit(x_data, y_data, 0.001)
        # bar = (
        #     Bar()
        #     .add_xaxis(x_data)
        #     .add_yaxis('价格出现概率占比', list(y_data)))
        # #     .set_global_opts(
        # #         xaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True)),  # 显示X轴分割线
        # #         yaxis_opts=opts.AxisOpts(name='概率/%', splitline_opts=opts.SplitLineOpts(is_show=True)),  # 显示Y轴分割线
        # #         title_opts=opts.TitleOpts(title=f"best_buy: {buy}\n\nbest_sell: {sell}\n\nprofit: {pro}", pos_right='10%', pos_top='10%')  # 显示标题
        # #     )
        # #     .set_series_opts(
        # #         label_opts=opts.LabelOpts(is_show=False),
        # #         markarea_opts=opts.MarkAreaOpts(
        # #             data=[
        # #                 opts.MarkAreaItem(name="", x=(str(buy), str(sell)), y=('0', str(y_data[buy_i]))),
        # #             ]))
        # # )
        # bar.render()

    def _max_profit(self, x_data: list, y_data: list, rate: float):
        """
        最大利润
        @param x_data: 价格
        @param y_data: 价格出现概率
        @param rate: 手续费率
        @return 利润概率，最小买入价下标，最大卖出价下标，最小买入价，最大卖出价
        """
        max_pro = 0  # 最大利润
        min_buy_i = 0  # 最小买单价下标
        max_sell_i = 0  # 最大卖单价下标
        min_sell_i = 0  # 最小卖单价下标
        for buy_i in range(0, len(x_data)):  # 遍历买单价格
            for sell_i in range(buy_i, len(x_data)):  # 根据费率计算找到有利润的最小卖单价下标
                if x_data[sell_i] - x_data[buy_i] - 2 * rate > 0:
                    min_sell_i = sell_i
                    break
            if min_sell_i == 0:  # 最小卖单价下标为0，说明全局不存在有利润的卖价，结束遍历
                return 0, 0, 0, 0, 0
            for sell_i in range(min_sell_i, len(x_data)):  # 从最小卖单价开始遍历，查找最大利润的最大卖单价下标
                if y_data[sell_i] >= y_data[buy_i]:  # 可卖出数量大于买入数量
                    pro = (x_data[sell_i] - x_data[buy_i]) * y_data[buy_i]  # 计算利润
                    if pro >= max_pro:  # 标记最大利润，最小买单下标，最大卖单下标
                        max_pro = pro
                        min_buy_i = buy_i
                        max_sell_i = sell_i
        return round(max_pro, 4), min_buy_i, max_sell_i, x_data[min_buy_i], x_data[max_sell_i]


if __name__ == '__main__':
    p = WssPredict()
    p.display_data()
    # r = RestPredict()
    # r.show()

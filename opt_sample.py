from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd # pandasデータフレームを使用


# Import the backtrader platform
import backtrader as bt
# from backtrader.analyzers import AnnualReturn

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('profit', 50),
        ('loss', 50),
        ('maperiod', 50),
        ('printlog', False),
        # ('weekday',1),
        ('deltama', 10),
        ('deltapnl',-2),
        ('tradehistorysumintupsize',1),
        ('tradehistorysumintdownsize',1),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod )

        self.tradehistory = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):

        _, isoweek, isoweekday = self.datetime.date().isocalendar()
        d_month = self.datetime.date().month
        d_day = self.datetime.date().day
        txt = '{},{},{}, Week {}, Day {}, O {}, H {}, L {}, C {}, position {},{},{}'.format(
            d_month,
            d_day,
            self.datetime.datetime(),
            isoweek, isoweekday,
            self.data.open[0], self.data.high[0],
            self.data.low[0], self.data.close[0],self.position.size, self.tradehistorynext[self.params.deltapnl:-1],self.tradehistorysumint 
        )
        # print(txt)

        self.lista = []
        self.listb = []

        longentrycondition = ((self.highest+ self.lowest)/2) <= self.data.close[0]
        shortentrycondition = ((self.highest+ self.lowest)/2) >= self.data.close[0]

        if self.tradehistorysumint > 0:
            if longentrycondition: 
                    if not self.position: # ポジションを持っていない場合
                        self.buy_bracket(size =self.params.tradehistorysumintupsize,limitprice= self.data.close[0]+ self.params.profit , price=self.data.close[0] , stopprice= self.data.close[0] - self.params.loss , tradeid = 1,valid=datetime.timedelta(hours=2,minutes= 00))

            if shortentrycondition:
                    if not self.position: # ポジションを持っている場合
                        self.sell_bracket(size =self.params.tradehistorysumintupsize,limitprice= self.data.close[0]-self.params.profit , price=self.data.close[0] , stopprice= self.data.close[0] + self.params.loss, tradeid = 1,valid=datetime.timedelta(hours=2,minutes= 00))


        if self.tradehistorysumint <= 0:
            if longentrycondition: 
                    if not self.position: # ポジションを持っていない場合
                        self.buy_bracket(size =self.params.tradehistorysumintdownsize,limitprice= self.data.close[0]+ self.params.profit , price=self.data.close[0] , stopprice= self.data.close[0] - self.params.loss , tradeid = 1,valid=datetime.timedelta(hours=2,minutes= 00))
            if shortentrycondition:
                if (self.data.datetime.time().hour ==13 and self.data.datetime.time().minute == 15):
                    if not self.position: # ポジションを持っている場合
                        self.sell_bracket(size =self.params.tradehistorysumintdownsize,limitprice= self.data.close[0]-self.params.profit , price=self.data.close[0] , stopprice= self.data.close[0] + self.params.loss, tradeid = 1,valid=datetime.timedelta(hours=2,minutes= 00))

        if (self.data.datetime.time().hour == 15) and (self.data.datetime.time().minute == 15) :
            if self.position:
                self.close(tradeid = 1) # ポジションをクローズする

    def stop(self):
        self.log('(profit %3d)(loss %3d)(maperiod %3d) Ending Value %.3f' %
                 (self.params.profit, self.params.loss, self.params.maperiod, self.broker.getvalue()), doprint=True)

    def notify_trade(self, trade): # 取引の開始/更新/終了を通知する
        if trade.isclosed: # トレードが完了した場合
            self.tradehistory.append(trade.pnl)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    strats = cerebro.optstrategy(
        TestStrategy,
        profit=range(50,51 ,50),
        loss=range(50, 51, 50),
        maperiod = range(50,201, 50),
        # weekday = range(1,6,1),
        deltama = range(10,51,10),
        deltapnl = range(-2,-5,-1),
        tradehistorysumintupsize = range(1,5,1),
        tradehistorysumintdownsize = range(1,5,1),
        )



    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    input_csv = os.path.join(os.getcwd(),'/Users/hayashikunita/python/backtrader1/NIkkei225-min15-TV-2021.csv')
    # input_csv = os.path.join(os.getcwd(),'/Users/hayashikunita/python/backtrader1/mmorley-14/Nikkei225-15min-2007-2020.csv')

    # csvファイルのフルパス
    df = pd.read_csv(input_csv) # csvファイルをPandasデータフレームに読み込む


    #日時列をdatatime型にしてインデックスにして、元の列は削除する
    df = df.set_index(pd.to_datetime(df['DateTime'])).drop('DateTime', axis=1) 

    import backtrader as bt # Backtrader
    import backtrader.feeds as btfeed # データ変換

    data = btfeed.PandasData(
        dataname=df, # PandasのデータをBacktraderの形式に変換する
        fromdate=datetime.datetime(2015, 1, 1),# 期間指定
        # todate=datetime.datetime(2020, 12, 31),# 期間指定
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.addanalyzer(bt.analyzers.DrawDown) # ドローダウン
    cerebro.addanalyzer(bt.analyzers.SQN) # SQN
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer) 

    # Set our desired cash start
    cerebro.broker.setcash(1000000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Run over everything
    results = cerebro.run(maxcpus=0)

# ================== 全て表示 ========================
    strats = [x[0] for x in results]  # flatten the result
    for i, strat in enumerate(strats):
        stratprofit = strat.params.profit
        stratloss = strat.params.loss
        stratmaperiod = strat.params.maperiod
        stratdeltama = strat.params.deltama
        sqn = strat.analyzers.sqn.get_analysis()
        dd  = strat.analyzers.drawdown.get_analysis()
        endingvalue = strat.analyzers.tradeanalyzer.get_analysis().pnl.net.total+1000000
        ana = strat.analyzers.tradeanalyzer.get_analysis()
        trades = strat.analyzers.tradeanalyzer.get_analysis().total.closed

        try:
            # pf = abs(ana.won.pnl.total / ana.lost.pnl.total)
            # winrate = ((ana.won.total / ana.total.closed) * 100)
            pf = abs(ana.won.pnl.total / ana.lost.pnl.total)
            winrate = ((ana.won.total / ana.total.closed) * 100)
        except ZeroDivisionError:
            pf = 0
            winrate = 0

        print('(profit {:>5d})(loss {:>5d})(maperiod {:>5d})(deltama {:>5d}) EndingValue: {:.2f} DrawDown: {} SQN: {:.3f} PF: {:.3f} Winrate: {:.3f} Trades:{:.3f}'
            .format(stratprofit,stratloss,stratmaperiod,stratdeltama,endingvalue,dd['max']['moneydown'],sqn['sqn'],pf,winrate,trades))

#＝＝＝＝＝＝＝＝＝＝＝＝＝＝ ランキング化 ＝＝＝＝＝＝＝＝＝＝＝＝＝＝

    strats = [x[0] for x in results]  # flatten the result

    profitlist = []
    losslist =[]
    periodlist = []
    deltamalist = []
    sqnlist = []
    ddlist = []
    endingvaluelist = []
    pflist = []
    winratelist = []
    tradeslist = []

    for i, strat in enumerate(strats):

        keys = ['profit', 'loss', 'period','deltama', 'sqn', 'dd', 'endingvalue', 'pf', 'winrate', 'weekday']

        stratprofit = strat.params.profit
        profitlist.append(stratprofit)
        
        stratloss = strat.params.loss
        losslist.append(stratloss)

        stratmaperiod = strat.params.maperiod
        periodlist.append(stratmaperiod)

        stratdeltama = strat.params.deltama
        deltamalist.append(stratdeltama)

        sqn = strat.analyzers.sqn.get_analysis()
        sqnlist.append(sqn['sqn'])

        dd  = strat.analyzers.drawdown.get_analysis()
        ddlist.append(dd['max']['moneydown'])

        endingvalue = strat.analyzers.tradeanalyzer.get_analysis().pnl.net.total+1000000
        endingvaluelist.append(endingvalue)

        ana = strat.analyzers.tradeanalyzer.get_analysis()

        trades = strat.analyzers.tradeanalyzer.get_analysis().total.closed
        tradeslist.append(trades)

        try:
            pf = abs(ana.won.pnl.total / ana.lost.pnl.total)
            winrate = ((ana.won.total / ana.total.closed) * 100)
        except ZeroDivisionError:
            pf = 0
            winrate = 0

        pflist.append(pf)
 
        winratelist.append(winrate)

    d1 = {'profit': profitlist, 'loss' : losslist, 'period': periodlist,'deltama' : deltamalist ,'sqn': sqnlist , 'dd' : ddlist, 'endingvalue' : endingvaluelist , 'pf': pflist , 'winrate': winratelist , 'trades': tradeslist} 
    d2={}
    for k,v in d1.items():   # 一度pd.Seriesに変換
        d2[k]=pd.Series(v)

    df=pd.DataFrame(d2)


    df['ev順位'] = df['endingvalue'].rank(ascending=False, method='min').astype('int')
    df['pf順位'] = df['pf'].rank(ascending=False, method='min').astype('int')
    df['wr順位'] = df['winrate'].rank(ascending=False, method='min').astype('int')
    df['dd順位'] = df['dd'].rank(ascending=True).astype('int')
    df['sqn順位'] = df['sqn'].rank(ascending=False, method='min').astype('int')
    df['total_score'] = df['endingvalue']*df['pf']*df['winrate']*(100000-df['dd'])*df['sqn']
    df['rank'] = df['total_score'].rank(ascending=False, method='min').astype('int')

    # ランキング別に、並べる
    df_sort = df.sort_values('rank', ascending=True).head(100)

    #行を全表示（行の数）
    pd.set_option("display.max_rows", 300)
    #列を全表示（列の数）
    pd.set_option("display.max_columns", 300)
    # 改行を無くす
    pd.set_option('display.expand_frame_repr', False)
    # pd.set_option('display.max_columns', None)
    print(df_sort)

    # 逆ランキング
    df_sort_false = df.sort_values('rank', ascending=False).head(50)
    print(df_sort_false)

#＝＝＝＝＝＝＝＝＝＝＝＝＝＝ ランキング化
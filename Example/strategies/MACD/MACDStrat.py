from AlphaPackage import *
from Example.strategies.benchmark.benchmark import *
import math
from AlphaPackage.MarketData import yahooClient
from AlphaPackage.Execution import alpha
from talib import MACD




class MACDStrat(Strategy):
    def __init__(self,fast_period=12,slow_period=26,signal_period=9):
        Strategy.__init__(self)
        self.verbose = False #
        self.in_market = False # by default the algo will begin with no positions and thus is not in the market
        self.trade_limits = (0.1,0.03) # set the trade limits
        self.parameter_dictionary = {'fastperiod':fast_period,'slowperiod':slow_period,'signalperiod':signal_period}

    def process_1(self):
        self.set_trade_allocation(0.7) # max cash to be used at any time for any asset

        cash_allocation = {} # cash allocation dictionary
        # cash to be used at any time for each asset
        for ticker in self.asset_dictionary.keys(): # iterate through the tickers in the asset universe
            cash_allocation[ticker] = self.trade_cash/len(self.asset_dictionary.keys()) # assign each asset an even cash allocation for trading

        # iterate through each asset in the universe and run trade Logic
        for ticker in self.asset_dictionary.keys():
            current_position = self.asset_dictionary[ticker].position # get the current size of the position from asset object
            self.in_market = True if current_position != 0 else False # varaible to tell if algo asset is risk on

            close = self.asset_dictionary[ticker].bars.Close # assign the current for loop asset's close price series to a temp variable
            macd, macdsignal, macdhist = MACD(close, fastperiod=self.parameter_dictionary['fastperiod'], slowperiod=self.parameter_dictionary['slowperiod'], signalperiod=self.parameter_dictionary['signalperiod']) # define our macd

            self.position_size = int(math.floor(cash_allocation[ticker] / close[-1])) # auto size our position

            if not self.in_market: # if not in the market then proceed to testing buy conditions
                if macdsignal[-1] > 0 and self.position_size > 0: # if fast > slow, buy the asset
                    self.create_order(ticker=ticker,quantity=self.position_size,price=close[-1],message='MACD BUY') # create the order
                    self.buy_price = close[-1] # set the buy price varible so we can use our offset / stop loss Logic
                else: pass

            elif self.in_market: # if in the market then proceed to testing sell conditions
                if macdsignal[-1] <= 0: # macd sell condition
                    self.create_order(ticker=ticker,quantity=-current_position,price=close[-1],message='MACD SELL') # create the order

                elif close[-1] >= self.buy_price*(1+self.trade_limits[0]): # offset stop sell
                    self.create_order(ticker=ticker, quantity=-current_position, price=close[-1],message='OFFSET STOP')# create the order

                elif close[-1] <= self.buy_price*(1-self.trade_limits[1]): # stop loss sell
                    self.create_order(ticker=ticker, quantity=-current_position, price=close[-1],message='STOP LOSS')# create the order

                else: pass
            else: pass


def main():
    COINS_TICKERS = ['USO','BNO','UGA','UNG','CORN','COW','SOYB','WEAT','JO','SGG','BAL','IAU','SLV','CPER']

    START_STOP_DATES = ('2020-7-15', '2021-7-19')  # define the start and stop dates

    for ticker in COINS_TICKERS:
        # get the data
        backtest_data = yahooClient.get_close_prices_yahoo(tickers=[ticker],  # tickers
                                                           start_date=START_STOP_DATES[0],  # start
                                                           stop_date=START_STOP_DATES[1])  # stop


        macd_strategy = MACDStrat(fast_period=12,slow_period=26,signal_period=9)  # define the strategy that will beat the sp500
        benchmark = BuyAndHold(allocation_dict={ticker:1})
        engine = alpha.Engine()  # define the engine that will test our epic win strat


        strategy_cumulative_returns = engine.backtest(strategy_object=macd_strategy,  # tell the engine what strategy we want to backtest
                                                      backtest_series_dictionary=backtest_data,  # tell the engine what data we want to backtest on
                                                      starting_cash=25000,  # set the starting cash
                                                      log=False,
                                                      filename='MACD_version1_LOG.csv')

        benchmark_cumulative_returns = engine.backtest(strategy_object=benchmark,# tell the engine what strategy we want to backtest
                                                      backtest_series_dictionary=backtest_data,# tell the engine what data we want to backtest on
                                                      starting_cash=25000, # set the starting cash
                                                      log=False,
                                                      filename='benchmark.csv')

        strategy_relative_return = strategy_cumulative_returns - benchmark_cumulative_returns

        print('Strategy - Benchmark returns %:',strategy_relative_return)




if __name__ == '__main__':
    main()


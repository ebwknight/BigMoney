# Go long at the close if today’s close is below yesterday’s five-day low.
# Sell at the close when the two-day RSI closes above 50.
# There is a time stop of five days if the sell criterium is not triggered.
import math
import numpy as np
import pandas as pd
from readData import get_data
from tech_ind import *
from backtest import assess_strategy
from OracleStrategy import OracleStrategy

#include MACD

class TechnicalStrategy:
    def __init__(self, *params, **kwparams):
        # Defined so you can call it with any parameters and it will just do nothing.
        pass

    def train(self, *params, **kwparams):
        # Defined so you can call it with any parameters and it will just do nothing.
        pass

    def test(self, start_date = '2018-01-01', end_date = '2019-12-31', symbol = ['DIS'], starting_cash = 200000):
        # Inputs represent the date range to consider, the single stock to trade, and the starting portfolio value.
        #
        # Return a date-indexed DataFrame with a single column containing the desired trade for that date.
        # Given the position limits, the only possible values are -2000, -1000, 0, 1000, 2000.

        # Read all the relevant s data (plus SPY) into a DataFrame.
        prices = get_data(start_date, end_date, symbol)
        spy_prices = get_data(start_date, end_date, ['SPY'])

        ### Calculate SMA-Five day low and RSI for the entire date range for all symbols.
        rsi = RSI(start_date, end_date, prices, 2)
        macd, signal, histogram = MACD(start_date, end_date, prices, window_size)
        bbp = BBands(start_date, end_date, prices, window_size)
        ### Use the three indicators to make some kind of trading decision for each day.

        # Trades starts as a NaN array of the same shape/index as price.
        trades = prices.copy()
        trades.loc[:,:] = np.NaN

        # Apply our entry order conditions all at once. 
        trades[(macd > signal) & (rsi < 15)] = 1
        trades[(macd < signal) & (rsi > 85) & (bbp > 0.5)] = -1

      # Apply our exit order conditions all at once.  Again, this represents TARGET SHARES.
        trades[(bbp > 0.9) & (rsi > 75)] = 0

        # Forward fill NaNs with previous values, then fill remaining NaNs with 0.
        trades.ffill(inplace=True)
        trades.fillna(0, inplace=True)

        # Now take the diff, which will give us an order to place only when the target shares changed.
        trades.iloc[1:] = trades.diff().iloc[1:]
        trades.iloc[0] = 0

        buy_y = []
        sell_y = []
        for day in trades.index:
          for sym in symbol:
            if trades.loc[day,sym] == 0:
              buy_y.append(np.nan)
              sell_y.append(np.nan)
            elif trades.loc[day,sym] > 0:
              buy_y.append(2)
              sell_y.append(np.nan)
            elif trades.loc[day,sym] < 0:
              sell_y.append(2)
              buy_y.append(np.nan)

        price_cols = list(prices)
        stock = price_cols[0]
        plt.bar(trades.index, buy_y, color='g')
        plt.bar(trades.index, sell_y, color='r')
        #plt.plot(prices[stock])
        # plt.plot(prices.index, buy_y, marker = '^', color = 'green', markersize = 5, label = 'BUY SIGNAL', linewidth = 0)
        # plt.plot(prices.index, sell_y, marker = 'v', color = 'r', markersize = 5, label = 'SELL SIGNAL', linewidth = 0)
        # plt.savefig('buy&sell')
        # And more importantly, drop all rows with no non-zero values (i.e. no trades).
        trades = trades.loc[(trades != 0).any(axis=1)]
        
        # Now we have only the days that have trades.  That's better, at least!


        # Compose the output trade list.
        trade_list = []
        

        for day in trades.index:
          for sym in symbol:
            if trades.loc[day,sym] > 0:
              trade_list.append([day.date(), sym, 'BUY', 1000])
            elif trades.loc[day,sym] < 0:
              trade_list.append([day.date(), sym, 'SELL', 1000])


        # Dump the trades to stdout.  (Redirect to a file if you wish.)
        for trade in trade_list:
          print ("	".join(str(x) for x in trade))

        trade_df = pd.DataFrame(trade_list, columns=['Date', 'Symbol', 'Direction', 'Shares'])
        print(trade_df)
        trade_df.to_csv('trades.csv')
        return trade_df

### Main function.  Not called if imported elsewhere as a module.
if __name__ == "__main__":

  start_date = '2010-01-01'
  end_date = '2021-12-31'
  symbols = ['DIS']
  window_size = 14

  T = TechnicalStrategy()
  T.test()
  prices = get_data(start_date, end_date, symbols)
  pval_df = assess_strategy()
  o = OracleStrategy()
  bline = o.test(start_date, end_date)
  print("\n")
  print(bline / bline.iloc[0])
  print("\n")
  print(pval_df / pval_df.iloc[0])
  plt.plot(bline / bline.iloc[0])
  plt.plot(pval_df / pval_df.iloc[0])
  plt.savefig('BaselineVsStrategy.png')


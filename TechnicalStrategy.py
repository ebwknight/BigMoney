# Go long at the close if today’s close is below yesterday’s five-day low.
# Sell at the close when the two-day RSI closes above 50.
# There is a time stop of five days if the sell criterium is not triggered.
import math
import numpy as np
import pandas as pd
from readData import get_data
from tech_ind import *
from backtest import *

class TechnicalStrategy:
    def __init__(self, *params, **kwparams):
        # Defined so you can call it with any parameters and it will just do nothing.
        pass

    def train(self, *params, **kwparams):
        # Defined so you can call it with any parameters and it will just do nothing.
        pass

    def test(self, start_date = '2018-01-01', end_date = '2019-12-31', symbol = 'DIS', starting_cash = 200000):
        # Inputs represent the date range to consider, the single stock to trade, and the starting portfolio value.
        #
        # Return a date-indexed DataFrame with a single column containing the desired trade for that date.
        # Given the position limits, the only possible values are -2000, -1000, 0, 1000, 2000.

        return df_trades

def build_trades (symbols, start_date, end_date, window_size):

  print (f"Constructing 5 Day low and RSI from {start_date} to {end_date}.")

  # Read all the relevant price data (plus SPY) into a DataFrame.
  price = get_data(start_date, end_date, symbols)

  # Add SPY to the symbol list for convenience.
  #symbols.append('SPY')


  ### Calculate SMA-Five day low and RSI for the entire date range for all symbols.
  fdl = x_day_low(start_date, end_date, symbols, window_size)
  rsi = RSI(start_date, end_date, symbols, window_size)
  symbols.remove('SPY')

  ### Use the three indicators to make some kind of trading decision for each day.

  # Trades starts as a NaN array of the same shape/index as price.
  trades = price.copy()
  trades.loc[:,:] = np.NaN

  # Apply our entry order conditions all at once.  This represents our TARGET SHARES
  # at this moment in time, not an actual order.
  ''' & (bbp < 0) & (rsi < 30) & (spy_rsi > 30)'''
  print(fdl)
  print(price)
  trades[(price <= fdl)] = 1000
  #trades[(sma > 1.05) & (bbp > 1) & (rsi > 70) & (spy_rsi < 70)] = -100

# Apply our exit order conditions all at once.  Again, this represents TARGET SHARES.
  trades[(rsi > 50)] = 0
#if there is a time stop of five days if the sell criterium is not triggered.
  days = 0
  for symbol in symbols:
    for index, row in trades.iterrows():
        if ((trades.loc[index, symbol] != (np.NaN)) and (trades.loc[index, symbol] != (0))):
            days = 0
        days += 1
        if days == 5:
            print('5 days since trade... bailing at ' + str(index))
            trades.loc[index, symbol] = 0

  print(trades.to_string())
  #exit_df = trades.rolling(window_size).any()
  #trades[(exit_df == False)] = 0
  #print(exit_df)

  # We now have -100, 0, or +100 TARGET SHARES on all days that "we care about".  (i.e. those
  # days when our strategy tells us something)  All other days are NaN, meaning "hold whatever
  # you have".

  # Forward fill NaNs with previous values, then fill remaining NaNs with 0.
  trades.ffill(inplace=True)
  trades.fillna(0, inplace=True)

  # We now have a dataframe with our TARGET SHARES on every day, including holding periods.

  # Now take the diff, which will give us an order to place only when the target shares changed.
  trades.iloc[1:] = trades.diff().iloc[1:]
  trades.iloc[0] = 0

  # And now we have our trades array, just as we wanted it, with no iteration.


  # It would be hard to vectorize our weird formatting output, which triggers on individual
  # elements and needs the index values (row and column).

  # But we can at least drop the SPY column.
#   del trades['SPY']
#   symbols.remove('SPY')

  # And more importantly, drop all rows with no non-zero values (i.e. no trades).
  trades = trades.loc[(trades != 0).any(axis=1)]

  # Now we have only the days that have trades.  That's better, at least!


  # Compose the output trade list.
  trade_list = []
  

  for day in trades.index:
    for sym in symbols:
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


### Main function.  Not called if imported elsewhere as a module.
if __name__ == "__main__":

  start_date = '2018-01-01'
  end_date = '2019-12-31'
  symbols = ['DIS']
  window_size = 7

  build_trades(symbols, start_date, end_date, window_size)
  pval_df = assess_strategy()


# Go long at the close if today’s close is below yesterday’s five-day low.
# Sell at the close when the two-day RSI closes above 50.
# There is a time stop of five days if the sell criterium is not triggered.
import math
import numpy as np
import pandas as pd
from readData import get_data
from tech_ind import *
from backtest import *

#include MACD

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

  # Read all the relevant s data (plus SPY) into a DataFrame.
  prices = get_data(start_date, end_date, symbols)
  spy_prices = get_data(start_date, end_date, ['SPY'])

  ### Calculate SMA-Five day low and RSI for the entire date range for all symbols.
  rsi = RSI(start_date, end_date, prices, 2)
  spy_rsi = RSI(start_date, end_date, spy_prices, window_size)
  macd, signal, histogram = MACD(start_date, end_date, prices, window_size)
  fdl = x_day_low(start_date, end_date, prices, 5)
  bbp = BBands(start_date, end_date, prices, window_size)
  sma_ratio = prices / SMA(start_date, end_date, prices, window_size)
  spy_sma_ratio = spy_prices / SMA(start_date, end_date, spy_prices, window_size)
  ### Use the three indicators to make some kind of trading decision for each day.

  # Trades starts as a NaN array of the same shape/index as price.
  trades = prices.copy()
  trades.loc[:,:] = np.NaN

  # Apply our entry order conditions all at once.  This represents our TARGET SHARES
  # at this moment in time, not an actual order.

  trades[(macd > signal)] = 1000
  trades[(macd < signal)] = -1000

# Apply our exit order conditions all at once.  Again, this represents TARGET SHARES.
  trades[(bbp > 0.3) & (rsi > 50)] = 0

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
  buy_y = []
  sell_y = []
  for day in trades.index:
    for sym in symbols:
      if trades.loc[day,sym] == 0:
        buy_y.append(np.nan)
        sell_y.append(np.nan)
      elif trades.loc[day,sym] > 0:
        buy_y.append(prices.loc[day,sym])
        sell_y.append(np.nan)
      elif trades.loc[day,sym] < 0:
        sell_y.append(prices.loc[day,sym])
        buy_y.append(np.nan)

  print(trades.to_string())
  price_cols = list(prices)
  stock = price_cols[0]
  plt.plot(prices[stock])
  plt.plot(prices.index, buy_y, marker = '^', color = 'green', markersize = 5, label = 'BUY SIGNAL', linewidth = 0)
  plt.plot(prices.index, sell_y, marker = 'v', color = 'r', markersize = 5, label = 'SELL SIGNAL', linewidth = 0)
  plt.savefig('buy&sell')
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
  window_size = 14

  build_trades(symbols, start_date, end_date, window_size)
  pval_df = assess_strategy()


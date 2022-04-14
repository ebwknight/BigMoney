import math
import numpy as np
import pandas as pd
from readData import get_data
from tech_ind import *
from backtest import *

def build_trades (symbols, start_date, end_date, lookback):

  print (f"Constructing SMA, BB%, RSI from {start_date} to {end_date}.")
# Add SPY to the symbol list for convenience.
  symbols.append('SPY')
  # Read all the relevant price data (plus SPY) into a DataFrame.
  price = get_data(start_date, end_date, symbols)

  


  ### Calculate SMA-14 for the entire date range for all symbols.
  sma = price.rolling(window=lookback,min_periods=lookback).mean()


  ### Calculate Bollinger Bands (14 day) over the entire period.
  rolling_std = price.rolling(window=lookback,min_periods=lookback).std()
  top_band = sma + (2 * rolling_std)
  bottom_band = sma - (2 * rolling_std)

  bbp = (price - bottom_band) / (top_band - bottom_band)


  ### Now we can turn the SMA into an SMA ratio, which is more useful.
  sma = price / sma


  ### Calculate Relative Strength Index (14 day) for the entire date range for all symbols.
  rsi = price.copy()

  # Pre-compute daily returns for repeated use.
  daily_rets = price.copy()
  daily_rets.values[1:,:] = price.values[1:,:] - price.values[:-1,:]
  daily_rets.values[0,:] = np.nan

  # Pre-compute up and down returns.
  up_rets = daily_rets[daily_rets >= 0].fillna(0).cumsum()
  down_rets = -1 * daily_rets[daily_rets < 0].fillna(0).cumsum()

  # Pre-compute up-day gains and down-day losses.
  up_gain = price.copy()
  up_gain.loc[:,:] = 0
  up_gain.values[lookback:,:] = up_rets.values[lookback:,:] - up_rets.values[:-lookback,:]

  down_loss = price.copy()
  down_loss.loc[:,:] = 0
  down_loss.values[lookback:,:] = down_rets.values[lookback:,:] - down_rets.values[:-lookback,:]

  # Now we can calculate the RS and RSI all at once.
  rs = (up_gain / lookback) / (down_loss / lookback)
  rsi = 100 - (100 / (1 + rs))
  rsi.iloc[:lookback,:] = np.nan

  # Inf results mean down_loss was 0.  Those should be RSI 100.
  rsi[rsi == np.inf] = 100


  ### Use the three indicators to make some kind of trading decision for each day.

  # Trades starts as a NaN array of the same shape/index as price.
  trades = price.copy()
  trades.loc[:,:] = np.NaN

  # Create a copy of RSI but with the SPY column copied to all columns.
  spy_rsi = rsi.copy()
  spy_rsi.values[:,:] = spy_rsi.loc[:,['SPY']]

  # Create a binary (0-1) array showing when price is above SMA-14.
  sma_cross = pd.DataFrame(0, index=sma.index, columns=sma.columns)
  sma_cross[sma >= 1] = 1

  # Turn that array into one that only shows the crossings (-1 == cross down, +1 == cross up).
  sma_cross.iloc[1:] = sma_cross.diff().iloc[1:]
  sma_cross.iloc[0] = 0

  # Apply our entry order conditions all at once.  This represents our TARGET SHARES
  # at this moment in time, not an actual order.
  trades[(sma < 0.95) & (bbp < 0) & (rsi < 30) & (spy_rsi > 30)] = 100
  trades[(sma > 1.05) & (bbp > 1) & (rsi > 70) & (spy_rsi < 70)] = -100

  # Apply our exit order conditions all at once.  Again, this represents TARGET SHARES.
  trades[(sma_cross != 0)] = 0

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
  del trades['SPY']
  symbols.remove('SPY')

  # And more importantly, drop all rows with no non-zero values (i.e. no trades).
  trades = trades.loc[(trades != 0).any(axis=1)]

  # Now we have only the days that have trades.  That's better, at least!

  # Compose the output trade list.
  trade_list = []

  for day in trades.index:
    for sym in symbols:
      if trades.loc[day,sym] > 0:
        trade_list.append([day.date(), sym, 'BUY', 100])
      elif trades.loc[day,sym] < 0:
        trade_list.append([day.date(), sym, 'SELL', 100])

  trade_df = pd.DataFrame(trade_list, columns=['Date', 'Symbol', 'Direction', 'Shares'])
  print(trade_df)
  trade_df.to_csv('trades.csv')
  # Dump the trades to stdout.  (Redirect to a file if you wish.)
  for trade in trade_list:
    print ("	".join(str(x) for x in trade))


### Main function.  Not called if imported elsewhere as a module.
if __name__ == "__main__":

  start_date = '2018-01-01'
  end_date = '2019-12-31'
  symbols = ['DIS']
  #symbols = ['HD']

  lookback = 14

  build_trades(symbols, start_date, end_date, lookback)
  pval_df = assess_strategy()


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_data(start_date, end_date, symbols, column_name = 'Adj Close', include_spy=True):

    dates = pd.date_range(start_date, end_date)
    df = pd.DataFrame(index=dates)

    if include_spy:
        df_new = pd.read_csv("../data/SPY.csv", index_col="Date", parse_dates=True, na_values=['nan'], usecols=['Date', column_name])
        df = df.join(df_new, how='inner')
        df = df.rename(columns={'Adj Close' : 'SPY'})
    else:
        df_new = pd.read_csv("../data/SPY.csv", index_col="Date", parse_dates=True, na_values=['nan'], usecols=['Date'])
        df = df.join(df_new, how='inner')

    for stock in symbols:

        df_new = pd.read_csv("../data/" + stock + ".csv", index_col="Date", parse_dates=True, na_values=['nan'], usecols=['Date', column_name])
        df = df.join(df_new, how='left') 
        df = df.rename(columns={'Adj Close' : stock})

    return df

def SMA(start_date, end_date, symbols, window_size):

    prices = get_data(start_date, end_date, symbols)
    symbols.append('SPY')
    sma = prices.rolling(window=window_size,min_periods=window_size).mean()
    #sma.dropna(inplace=True)
    #print(sma)
    return sma

def BBands(start_date, end_date, symbols, window_size):
    prices = get_data(start_date, end_date, symbols)
    sma = SMA(start_date, end_date, symbols, window_size)
    symbols.append('SPY')
    rolling_std = prices.rolling(window=window_size,min_periods=window_size).std()
    top_band = sma + (2 * rolling_std)
    bottom_band = sma - (2 * rolling_std)
    bbp = (prices - bottom_band) / (top_band - bottom_band)
    print(bbp)
    return bbp

def RSI(start_date, end_date, symbols, window_size):
    prices = get_data(start_date, end_date, symbols)
    sma = SMA(start_date, end_date, symbols, window_size)
    # Now we can calculate the RS and RSI all at once.
    rsi = prices.copy()
    # Pre-compute daily returns for repeated use.
    daily_rets = prices.copy()
    daily_rets.values[1:,:] = prices.values[1:,:] - prices.values[:-1,:]
    daily_rets.values[0,:] = np.nan
    # Pre-compute up and down returns.
    up_rets = daily_rets[daily_rets >= 0].fillna(0).cumsum()
    down_rets = -1 * daily_rets[daily_rets < 0].fillna(0).cumsum()
    # Pre-compute up-day gains and down-day losses.
    up_gain = prices.copy()
    up_gain.loc[:,:] = 0
    up_gain.values[window_size:,:] = up_rets.values[window_size:,:] - up_rets.values[:-window_size,:]
    down_loss = prices.copy()
    down_loss.loc[:,:] = 0
    down_loss.values[window_size:,:] = down_rets.values[window_size:,:] - down_rets.values[:-window_size,:]

    rs = (up_gain / window_size) / (down_loss / window_size)
    rsi = 100 - (100 / (1 + rs))
    rsi.iloc[:window_size,:] = np.nan

    # Inf results mean down_loss was 0.  Those should be RSI 100.
    rsi[rsi == np.inf] = 100
    print(rsi)
    figure, axis = plt.subplots(2, 1)
    axis[0].plot(prices[symbols[0]])
    axis[0].set_title("Normal Prices")
    axis[1].plot(rsi[symbols[0]])
    axis[1].set_title("RSI")
    plt.savefig('RSI')
    return rsi

def x_day_low(start_date, end_date, symbols, window_size):
    prices = get_data(start_date, end_date, symbols)
    lows = prices.rolling(window_size, min_periods=1).min()
    figure, axis = plt.subplots(2, 1)
    axis[0].plot(prices[symbols[0]])
    axis[0].set_title("Normal Prices")
    axis[1].plot(lows[symbols[0]])
    axis[1].set_title("5 Day Lows")
    plt.savefig('X Day Low')
    return lows


def main():
    lows = x_day_low('2018-01-01','2019-12-31',['AAPL','JPM','TSLA'], 14)
    print(lows)
  
if __name__=="__main__":
    main()
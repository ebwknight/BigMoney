from matplotlib.pyplot import fill
import numpy as np
import pandas as pd

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

class OracleStrategy:
    def __init__(self, *params, **kwparams):
        # Defined so you can call it with any parameters and it will just do nothing.
        pass

    def train(self, *params, **kwparams):
        # Defined so you can call it with any parameters and it will just do nothing.
        pass

    def test(start_date = '2018-01-01', end_date = '2019-12-31', symbol = 'DIS', starting_cash = 200000):
        # Inputs represent the date range to consider, the single stock to trade, and the starting portfolio value.
        #
        # Return a date-indexed DataFrame with a single column containing the desired trade for that date.
        # Given the position limits, the only possible values are -2000, -1000, 0, 1000, 2000.

        prices = get_data(start_date, end_date, [symbol])
        prices['Tomorrow'] = prices['DIS'].shift(periods=-1)

        return df_trades

def main():
    prices = get_data('2018-01-01', '2019-12-31', ['DIS'])
    prices['Tomorrow'] = prices['DIS'].shift(periods=-1)
    prices['Signal'] = prices['Tomorrow'] - prices['DIS']
    prices['Cash'] = 200000
    prices['Holdings'] = 0
    prices['Trades'] = 0

    prev_index = None
    for index, row in prices.iterrows():
        if prev_index != None:
            prices.loc[index, 'Cash'] = prices.loc[prev_index, 'Cash']
            prices.loc[index, 'Holdings'] = prices.loc[prev_index, 'Holdings']
        if row['Signal'] > 0:
            if (row['Cash'] / row['DIS']) >= 2000:
                prices.loc[index,'Trades'] = 2000
                prices.loc[index,'Cash'] -= (2000 * row['DIS'])
                prices.loc[index,'Holdings'] += 2000
            elif (row['Cash'] / row['DIS']) >= 1000:
                prices.loc[index,'Trades'] = 1000
                prices.loc[index,'Cash'] -= (1000 * row['DIS'])
                prices.loc[index,'Holdings'] += 1000
        else:
            if prices.loc[index, 'Holdings'] >= 2000:
                prices.loc[index,'Trades'] = -2000
                prices.loc[index,'Cash'] += (2000 * row['DIS'])
                prices.loc[index,'Holdings'] -= 2000
            if prices.loc[index, 'Holdings'] >= 1000:
                prices.loc[index,'Trades'] = -1000
                prices.loc[index,'Cash'] += (1000 * row['DIS'])
                prices.loc[index,'Holdings'] -= 1000
        prev_index = index
    print(prices.to_string())
  
if __name__=="__main__":
    main()
import pandas as pd
import numpy as np
from math import sqrt
import matplotlib
import matplotlib.pyplot as plt
from readData import get_data


def assess_portfolio (portfolio, starting_value=200000, risk_free_rate=0.0,
                      sample_freq=252, plot_returns=False):

    cumulative_return = ((portfolio.iloc[-1]) / starting_value) - 1
    end_value = (cumulative_return + 1) * starting_value
    daily_returns = ((portfolio / portfolio.shift()) - 1)
    average_daily_return = daily_returns.mean()
    stdev_daily_return = daily_returns.std()
    sharpe_ratio = sqrt(sample_freq) * (average_daily_return - risk_free_rate) / stdev_daily_return

    print("Sharpe Ratio: " + str(sharpe_ratio))
    print("Volatility: " + str(stdev_daily_return))
    print("Average Daily Return: " + str(average_daily_return))
    print("Cumulative Return: " + str(cumulative_return))
    print("End value: " + str(end_value))

    if plot_returns:

        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        normalized_df = df / df.iloc[0]
        normalized_df[['SPY', 'Portfolio']].plot()
        plt.title('Daily portfolio value vs SPY')
        plt.savefig('PortfolioVsSPY.png')
        plt.close()

    return sharpe_ratio, stdev_daily_return, average_daily_return, cumulative_return, end_value

def assess_strategy(trade_file = "trades.csv", starting_value = 200000, fixed_cost = 9.95, floating_cost = 0.005):

    trade_df = pd.read_csv(trade_file, index_col="Date", parse_dates=True, na_values=['nan'])
    #print(trade_df)
    start_date = trade_df.index[0]
    end_date = trade_df.index[len(trade_df)-1]
    price_df = get_data(start_date, end_date, trade_df.Symbol.unique())
    price_df['CASH'] = 1

    #create df of allocations
    alloc_df = pd.DataFrame(0, index=price_df.index, columns=trade_df.Symbol.unique())
    alloc_df['CASH'] = starting_value
    #print(alloc_df)

    for i in range(len(trade_df)):
        action = trade_df.iloc[i]['Direction']
        ticker = trade_df.iloc[i]['Symbol']
        shares = trade_df.iloc[i]['Shares']
        date = trade_df.index[i]
        value = price_df.at[trade_df.index[i], ticker]
        if action == 'BUY':
            #print(f"Buying {shares} shares of {ticker}...")
            alloc_df.loc[date:, ticker] += shares
            alloc_df.loc[date:, 'CASH'] -= ((shares * value) + fixed_cost + (shares * value * floating_cost))
            #print(alloc_df)
        elif action == 'SELL':
            #print(f"Selling {shares} shares of {ticker}...")
            alloc_df.loc[date:, ticker] -= shares
            alloc_df.loc[date:, 'CASH'] += ((shares * value) - fixed_cost - (shares * value * floating_cost))
            #print(alloc_df)
    
    pval_df = (price_df * alloc_df).sum(axis=1)
    print('\n')
    print(pval_df)
    print("Start Date: " + str(start_date))
    print("End Date: " + str(end_date))
    assess_portfolio(pval_df)
    return pval_df


# def main():
#     stats = assess_strategy()
#     print(stats)
  
# if __name__=="__main__":
#     main()
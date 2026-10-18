# Importing Libraries 

import pandas as pd 
import numpy as np
from core.fetch import load_clean
from core.indicators import compute_bollinger
import matplotlib.pyplot as plt 
#--------------------------------------------------------------#

# Global Variables 
TICKER = 'BTC-USD'
START = "2020-01-02"
END = "2026-01-01"
PERIOD = 20
NUM_STD = 2
FEES = 0.1
#--------------------------------------------------------------#

# Loads validated and cleaned asset data
df = load_clean(TICKER, START, END)
df = compute_bollinger(df, PERIOD, NUM_STD)
#--------------------------------------------------------------#

# Generates buy/sell signals 
def generate_signals(df, period):
    trade_active = False

    trades = []

    for i in range(period, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]
        #--------------------------------------------------------------#

        # If NOT in a trade 
        if not trade_active:
            
            # Enter long 
            if yesterday['low'] < yesterday['bb_lower']:
                direction = 'long'
                entry = today['open']
                entry_date = df.index[i]
                stop = yesterday['low'] * 0.995
                target_mid = yesterday['bb_middle']
                target_far = yesterday['bb_upper']
                trade_active = True
                remaining_size = 1.0
                t1_hit = False 

            # Enter short
            elif yesterday['high'] > yesterday['bb_upper']:
                direction = 'short'
                entry = today['open']
                entry_date = df.index[i]
                stop = yesterday['high'] * 1.005
                target_mid = yesterday['bb_middle']
                target_far = yesterday['bb_lower']
                trade_active = True
                remaining_size = 1.0
                t1_hit = False 
        #--------------------------------------------------------------#

        # If IN a trade:
        if trade_active:

        # Stops hit 

            # long stop hit 
            if direction == 'long':
                if today['low'] <= stop:
                    trade_active = False
                    exit_date = df.index[i]
                    trade_duration_days = exit_date - entry_date
                    size_closed = remaining_size
                    pnl = ((stop - entry)/entry) * 100
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": stop, 
                        "Duration(days)": trade_duration_days,
                        "Size Closed": size_closed,
                        "Reason": "Stop",
                        "PnL(%)": pnl 
                    })
                    continue

            # short stop hit 
            else:
                if today['high'] >= stop:
                    trade_active = False
                    exit_date = df.index[i]
                    trade_duration_days = exit_date - entry_date
                    size_closed = remaining_size
                    pnl = ((entry - stop)/entry) * 100
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": stop, 
                        "Duration(days)": trade_duration_days,
                        "Size Closed": size_closed,
                        "Reason": "Stop",
                        "PnL(%)": pnl 
                    })
                    continue
            #--------------------------------------------------------------#

        # Targets hit 

            # Case: longs hit 
            if direction == 'long':

                # Case 1: when target 1 hits and stop moves to entry 
                if not t1_hit and today['high'] >= target_mid:
                    t1_hit = True
                    size_closed = 0.5 
                    target1_exit_date = df.index[i]
                    exit_price = target_mid
                    remaining_size = size_closed
                    stop = entry
                    trade_duration_days = target1_exit_date - entry_date
                    pnl = ((target_mid - entry)/entry) * 100 
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": target1_exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": trade_duration_days,
                        "Size Closed": size_closed,
                        "Reason": "Target 1",
                        "PnL(%)": pnl 
                    })

                # Case 2: when both targets are hit 
                if t1_hit and today['high'] >= target_far:
                    trade_active = False 
                    exit_date = df.index[i]
                    exit_price = target_far
                    trade_duration_days = exit_date - entry_date 
                    size_closed = remaining_size
                    pnl = ((target_far - entry)/entry) * 100
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": trade_duration_days,
                        "Size Closed": size_closed,
                        "Reason": "Target 2",
                        "PnL(%)": pnl 
                    })

            # Case: shorts hit 
            if direction == 'short':

                # Case 1: when target 1 hits and stop moves to entry 
                if not t1_hit and today['low'] <= target_mid:
                    t1_hit = True
                    target1_exit_date = df.index[i]
                    exit_price = target_mid
                    size_closed = 0.5
                    remaining_size = size_closed
                    trade_duration_days = target1_exit_date - entry_date
                    stop = entry
                    pnl = ((entry - target_mid)/entry) * 100 
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": target1_exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": trade_duration_days,
                        "Size Closed": size_closed,
                        "Reason": "Target 1",
                        "PnL(%)": pnl 
                    })

                # Case 2: when both targets are hit 
                if t1_hit and today['low'] <= target_far:
                    trade_active = False 
                    exit_date = df.index[i]
                    exit_price = target_far
                    trade_duration_days = exit_date - entry_date 
                    size_closed = 0.5
                    remaining_size = 0.0
                    pnl = ((entry - target_far)/entry) * 100
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": trade_duration_days,
                        "Size Closed": size_closed,
                        "Reason": "Target 2",
                        "PnL(%)": pnl 
                    })

    return pd.DataFrame(trades)
#--------------------------------------------------------------#

# Generates the trades table
trades = generate_signals(df, PERIOD)

# Computes Net PnL (taking into account fees)
trades['Net PnL(%)'] = trades['PnL(%)'] - FEES 
#--------------------------------------------------------------#

# Computes stats on the trades column 
def compute_metrics(trades):

    # Creates a new column, Contribution that calculates the total contribuion of each row to the trade 
    trades['Contribution'] = trades['Size Closed'] * trades['Net PnL(%)']

    # Sums up the total pnl of that particular contribution 
    per_trades = trades.groupby('Entry Date')['Contribution'].sum()

    # Basic trade stats
    total_trades = len(per_trades)
    win_rate = (per_trades > 0).mean() * 100
    avg_win = per_trades[per_trades > 0].mean()
    avg_loss = per_trades[per_trades <= 0].mean()
    expectancy = per_trades.mean()

    return ({
        "Number of trades": total_trades,
        "Win Rate (%)": float(round(win_rate, 2)),
        "Average Win (%)": float(round(avg_win, 2)),
        "Average Loss (%)": float(round(avg_loss, 2)),
        "Expectancy (%)": float(round(expectancy, 2)),
        "Longest Trades Duration (days)": trades.sort_values('Duration(days)', ascending=False).head(10)
    })
#--------------------------------------------------------------#

# Delivers results to the terminal 
results = compute_metrics(trades)
print(results)
#--------------------------------------------------------------#

# Equity Curve & Max Drawdown 
sorted_trades = trades.sort_values(by='Exit Date')
sorted_trades['Growth Factor'] = 1 + sorted_trades['Contribution']/100 
equity = sorted_trades['Growth Factor'].cumprod()
buy_hold = df['close'] / df['close'].iloc[0]
#--------------------------------------------------------------#

# Computes max drawdown 
def max_drawdown(series):
    running_peak = series.cummax()
    drawdown = series/running_peak - 1
    return drawdown.min() * 100 
#--------------------------------------------------------------#
# Generates charts/visuals 

plt.figure(figsize=(12, 6))
plt.plot(sorted_trades['Exit Date'], equity, label='Strategy')
plt.plot(df.index, buy_hold, label='Buy and Hold BTC')
plt.legend()
plt.title("Equity Curve: BB Mean Reversion vs Buy and Hold")
plt.ylabel("Growth of $1")
plt.yscale('log')
plt.show()
#--------------------end-of-code-------------------------------#
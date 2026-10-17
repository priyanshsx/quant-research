#----------------to-delete-below-------------------------------#

# strategy: bollinger bands mean reversion
# what it does: computes the bb bands for the past 7 days, then opens a long when a D1 candle wicks below 
# the computed bb band and/or opens a short when the D1 candle wicks beyond the bb high 
# Bands: BB low, BB high
# Long signal: yesterday's D1 candle wick below the 7D BB low band
# Short signal: yesterday's D1 candle wick above the 7D BB high band
# entry: today's open
# exit: 50% at bb middle and 50% at bb high 
# stop-loss: none in v1 
# costs: fixed % 
# what if a new signal fires if already in a trade: stick to the ongoing trade 
#----------------to-delete-above-------------------------------#


# Importing Libraries 

import pandas as pd 
from core.fetch import load_clean
from core.indicators import compute_bollinger
import matplotlib.pyplot as plt 
#--------------------------------------------------------------#

# Loads validated and cleaned asset data
df = load_clean("BTC-USD", "2020-01-01", "2026-01-01")
df = compute_bollinger(df)
#--------------------------------------------------------------#

# Generates charts/visuals 
window = df.loc["2025-01":"2026-01"]

# plt.figure(figsize=(12,6))
# plt.plot(window.index, window['close'], label='Close', color='black')
# plt.plot(window.index, window['bb_middle'], label='Middle', linestyle='--')
# plt.plot(window.index, window['bb_upper'], label='Upper')
# plt.plot(window.index, window['bb_lower'], label='Lower')
# plt.legend()
# plt.title("BTC-USD with Bollinger Bands (20, 2)")
# plt.show()

# Generates buy/sell signals 
def generate_signals(df):
    trade_active = False

    trades = []

    for i in range(20, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]

        # if not in a trade 

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
                print(f"Long details: {entry_date}, {direction}, {entry}, {stop}, {target_mid}, {target_far}")

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
                print(f"Short Details: {entry_date}, {direction}, {entry: .2f}, {stop: .2f}, {target_mid: .2f}, {target_far: .2f}")
        #--------------------------------------------------------------#

        # if in a trade:
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
                    print(f"SL hit. Close date: {exit_date}, Exit Price: {stop: .2f}, Duration(days): {trade_duration_days}, Size Closed: {size_closed}, PnL(%): {pnl}")
                    continue

            # short stop hit 
            else:
                if today['high'] >= stop:
                    trade_active = False
                    exit_date = df.index[i]
                    trade_duration_days = exit_date - entry_date
                    size_closed = remaining_size
                    pnl = ((entry - stop)/entry) * 100
                    print(f"SL hit. Close date: {exit_date}, Exit Price: {stop}, Duration(days): {trade_duration_days}, Size Closed: {size_closed}, PnL(%): {pnl}")
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
                    remaining_size = size_closed
                    stop = entry
                    pnl = ((target_mid - entry)/entry) * 100 
                    print(f"Target 1(mid) hit: Exit Date: {target1_exit_date}, Size Closed: {size_closed}, PnL(%): {pnl}")

                # Case 2: when both targets are hit 
                if t1_hit and today['high'] >= target_far:
                    trade_active = False 
                    exit_date = df.index[i]
                    trade_duration_days = exit_date - entry_date 
                    size_closed = remaining_size
                    pnl = ((target_far - entry)/entry) * 100
                    print(f"All targets hit. Close date: {exit_date}, Duration(days): {trade_duration_days}, PnL(%): {pnl}")

            # Case: shorts hit 
            if direction == 'short':

                # Case 1: when target 1 hits and stop moves to entry 
                if not t1_hit and today['low'] <= target_mid:
                    t1_hit = True
                    target1_exit_date = df.index[i]
                    size_closed = 0.5
                    remaining_size = size_closed
                    stop = entry
                    pnl = ((entry - target_mid)/entry) * 100 
                    print(f"Target 1(mid) hit: Exit Date: {target1_exit_date}, Size Closed: {remaining_size}, PnL(%): {pnl}")

                # Case 2: when both targets are hit 
                if t1_hit and today['low'] <= target_far:
                    trade_active = False 
                    exit_date = df.index[i]
                    trade_duration_days = exit_date - entry_date 
                    size_closed = 0.0
                    remaining_size = size_closed
                    pnl = ((entry - target_far)/entry) * 100
                    print(f"All targets hit. Close date: {exit_date}, Size Closed: {size_closed}, Duration(days): {trade_duration_days}, PnL(%): {pnl}")
#--------------------------------------------------------------#

print_signal = generate_signals(df)
print(df.loc["2024-03-10":"2024-03-20", ['open', 'high', 'low', 'close', 'bb_lower', 'bb_middle', 'bb_upper']])


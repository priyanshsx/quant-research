# Importing Libraries 

import pandas as pd 
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
#--------------------------------------------------------------#

# Loads validated and cleaned asset data
df = load_clean(TICKER, START, END)
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
                    pnl = ((target_mid - entry)/entry) * 100 
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": target1_exit_date,
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
                        "Duration(days)": exit_date,
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
                    stop = entry
                    pnl = ((entry - target_mid)/entry) * 100 
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": target1_exit_date,
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
                    size_closed = 0.0
                    remaining_size = size_closed
                    pnl = ((entry - target_far)/entry) * 100
                    trades.append({
                        "Entry Date": entry_date,
                        "Exit Date": exit_date,
                        "Direction": direction,
                        "Entry Price": entry,
                        "Exit Price": exit_price, 
                        "Duration(days)": exit_date,
                        "Size Closed": size_closed,
                        "Reason": "Target 2",
                        "PnL(%)": pnl 
                    })

    return pd.DataFrame(trades)
#--------------------------------------------------------------#

trades = generate_signals(df, PERIOD)
print(trades)

#--------------------end-of-code-------------------------------#
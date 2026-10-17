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
import numpy as np 
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

plt.figure(figsize=(12,6))
plt.plot(window.index, window['close'], label='Close', color='black')
plt.plot(window.index, window['bb_middle'], label='Middle', linestyle='--')
plt.plot(window.index, window['bb_upper'], label='Upper')
plt.plot(window.index, window['bb_lower'], label='Lower')
plt.legend()
plt.title("BTC-USD with Bollinger Bands (20, 2)")
plt.show()

# Generates buy/sell signals 
def generate_signals(df):
    # add a column signal: 1 = enter long, -1: enter short,
    # 0 = exit, NaN = No new information 

    # guidelines 
    # Long signal: yesterday's D1 candle wicks below the BB low band; long today's open
    # Short signal: yesterday's D1 candle wicks above the BB upper band; short today's open 
    # exit: 50% at bb middle, 50% at bb upper/lower (these exits should be calculated based on band values from the signal day)
    # if a trade is already active, no other trades can be suggested by the strategy 
    # short stop: stop just above the signal high * 1.005 
    # long stop: stop just below the signal low * 0.995 of price 
    # after the 50% target hit, stops move to breakeven 
    
    # Structure
    # for each day (starting from the inception of the bands):
        # if in a trade:
            # using today's/yesterday's high and low, check: 
                # was the stop hit? 
                    # if true, close anything left 
                
                # was target 1 hit? 
                    # close half, move stop to entry
                
                # was target 2 hit? 
                    # close the rest, record the trade 
        
        # if not in a trade:
            # look at yesterday's candle and bands:
                # low below lower band? 
                    # enter long at today's open
                    # set stop and targets
                
                # high above upper band? 
                    # enter short at today's open 
                    # set stop and targets 

    trade_active = False

    for i in range(20, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]

        # if in a trade:
        # yet to be written 

        # if not in a trade 
        if not trade_active:
            if yesterday['low'] < yesterday['bb_lower']:
                direction = 'long'
                entry = today['open']
                stop = yesterday['low'] * 0.995
                target_mid = yesterday['bb_middle']
                target_far = yesterday['bb_upper']
                print(f"Long details: {df.index[i]}, {direction}, {entry}, {stop}, {target_mid}, {target_far}")
            
            elif yesterday['high'] > yesterday['bb_upper']:
                direction = 'short'
                entry = today['open']
                stop = yesterday['high'] * 1.005
                target_mid = yesterday['bb_middle']
                target_far = yesterday['bb_lower']
                print(f"Short Details: {df.index[i]}, {direction}, {entry}, {stop}, {target_mid}, {target_far}")
#--------------------------------------------------------------#

print_signal = generate_signals(df)
print(print_signal)


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
#--------------------------------------------------------------#

# Loads validated and cleaned asset data
df = load_clean("BTC-USD", "2020-01-01", "2026-01-01")
#--------------------------------------------------------------#

# Computes bollinger bands
def add_bollinger_bands(df):
    # based on the data from above function, we compute the bollinger bands 
    # columns: bb_mid, bb_upper, bb_lower
    pass
#--------------------------------------------------------------#

# Generates buy/sell signals 
def generate_signals(df):
    # add a column signal: 1 = enter long, -1: enter short,
    # 0 = exit, NaN = No new information 
    pass
#--------------------------------------------------------------#

# Offers details on positions (long/short)
def compute_positions(df):
    # turn signals into a 'position' column held day to day 
    pass 
#--------------------------------------------------------------#

# 
def compute_returns(df, cost_per_trade=0.001):
    # add 'strategy_ret' and 'equity' columns
    pass
#--------------------------------------------------------------#

def evaluate(df):
    # print the summary metrics 
    pass 
#--------------------------------------------------------------#



# Imports Libraries 

import pandas as pd
#--------------------------------------------------------------#

# Computes the bollinger bands 
def compute_bollinger(df, period=20, num_std=2):

    # Computes the middle band
    # 20-day SMA 
    df['bb_middle'] = df['close'].rolling(window=period).mean()

    #20-day stdev of the close 
    df['stdev'] = df['close'].rolling(window=period).std(ddof=0)

    # Computes the upper band 
    df['bb_upper'] = df['bb_middle'] + (num_std * df['stdev'])

    # Computes the lower band
    df['bb_lower'] = df['bb_middle'] - (num_std * df['stdev'])

    return df 
#--------------------------------------------------------------#
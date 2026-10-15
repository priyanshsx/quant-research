import pandas as pd 
import yfinance as yf
#--------------------------------------------------------------#

# downloads data from yahoo finance 
def fetch_asset(ticker, start_date, end_date):

   # downloads the raw data 
   asset = yf.download(ticker, start=start_date, end=end_date)

   # handles if yf.download did not work/failed 
   if asset.empty:
     raise ValueError(f"No data returned for {ticker} between {start_date} and {end_date}.")
    
   # formats the columns into a standard from the raw downloaded data   
   asset.columns = asset.columns.droplevel(1).str.lower()
   asset.index.name = 'date'
   asset.columns.name = None 
   return asset 
#--------------------------------------------------------------#

def validate(df):
   duplicates = df.index.duplicated(keep="first")
   num_duplicates = duplicates.sum()
   if num_duplicates > 0:
      df = df[~duplicates]
      print(f"Warning: dropped {num_duplicates} duplicate dates.")

   # checking for missing dates 
   calendar = pd.date_range(start=df.index.min(), end=df.index.max())
   missing_dates = calendar.difference(df.index)

   # checking for corrupted highs and lows where low > high 
   corrupted_high_low = df[df['low'] > df['high']]

   # checking for where volume is below 0 
   negative_volume = df[df['volume'] < 0]

   # checking for where high vs. open/close check 
   high_open_close = df[(df['open'] > df['high']) | (df['close'] > df['high'])]
   low_open_close = df[(df['low'] > df['open']) | (df['close'] < df['low'])]

   # checking for price columns
   price_cols = ["open", "high", "low", "close"]
   nan_rows = df[df[price_cols].isna().any(axis=1)]

   # empty list to track errors 
   errors = []

   # error check 
   if len(missing_dates) > 0:
      print(f"Warning: found {len(missing_dates)} missing dates, which are: {missing_dates}.")
   if len(nan_rows) > 0:
      errors.append(f"Found {len(nan_rows)} rows with missing prices on: {list(nan_rows.index.date)}")
   if len(corrupted_high_low) > 0:
      errors.append(f"Found corrupted highs/lows: {len(corrupted_high_low)}: {corrupted_high_low}")
   if len(negative_volume) > 0: 
      errors.append(f"Found negative volume entries: {len(negative_volume)}: {negative_volume}")
   if len(high_open_close) > 0 or len(low_open_close) > 0:
      errors.append(f"Found bad data on high and low closes. Where open > high or close > high: {len(high_open_close)}. Where low > open or close < low: {len(low_open_close)}. Please check before proceeding.")

   if len(errors) == 0:
      return df 
   else:
      message = "\n".join(errors)
      raise ValueError(f"Bad data found:\n{message}")
#--------------------------------------------------------------#

# calling both the functions to output the validated_data for strategies 
def load_clean(ticker, start_date, end_date):
   downloaded_asset = fetch_asset(ticker, start_date, end_date)
   validated_data = validate(downloaded_asset)

   return validated_data
#--------------------------------------------------------------#

if __name__ == "__main__":
   df = load_clean("BTC-USD", "2019-01-01", "2025-01-01")
   df.info()
   print(df.head())
#--------------------------------------------------------------#
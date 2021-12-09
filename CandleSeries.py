import pandas as pd
import logging
import datetime
from FTXClient import FTXClient
from typing import Dict

# Map interval duration to a pandas datetime type (used by _ts_trunc)
_RES_DT_TYPE_MAP = {
    60: "min",
    3600: "H",
    86400: "D"
}

# Class CandleSeries
# CandleSeries objects will contain ohlc candlestick data for a specified market and resolution
# Provides functionality to update ohlc data with new trade data
# When a candle interval ends, checks to see if internally kept data matches FTX data and logs any differences. 
# Also fetches open interest.
# Constructor args:
#   market - name of the market
#   resolution - candle interval length - options: 15, 60, 300, 900, 3600, 14400, 86400, or any multiple of 86400 up to 30*86400
#   history - optional, to load number of periods in history on instantiation, default 3
class CandleSeries():
    def __init__(self, market:str, resolution:int, history:int=3):
        self.market = market
        self.resolution = resolution
        self.candle_data = FTXClient.get_historical_ohlc(market, resolution, history)

    def __str__(self):
        return self.candle_data.iloc[-5:].to_string()

    def dump_to_csv(self):
        epoch_now = ( (datetime.datetime.now() - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s"))
        filename = f"{epoch_now}_{self.market}_{self.resolution}sec_candle_data.csv"
        self.candle_data.to_csv(filename)
        logging.info(f"Candle data written to {filename}.")

    # Function _ts_trunc    
    # Floors a string timestamp to the start of it's candle interval.
    # Uses pd timestamp datatype and pd floor() to do this.
    # pd timestamp objects can be non-performant. If realtime volume is very high (1000s per second), this would need to be optimized.
    # Currently only minute, hour and day are supported. By enhancing this function, we can support other resolutions.
    def _ts_trunc(self, ts):
        #convert to pd timestamp
        pd_ts = pd.to_datetime(ts)
        try:
            _trunc_ts = pd_ts.floor(_RES_DT_TYPE_MAP[self.resolution])
        except Exception as e:
            logging.error(f"Could not determine candle interval for timestamp. Possibly unsupported resolution requested.")
            raise e
        else:
            return _trunc_ts


    def get_latest_interval(self):
        ts_string = self.candle_data.iloc[-1].name
        return pd.to_datetime(ts_string)

    def get_interval_data(self, interval_start):
        return self.candle_data.loc[interval_start]

    
    # Function update
    # Takes a new trade and updates candle data
    # Inputs:
    #   new_trade - dictionary with keys time, price, size 
    def update(self, new_trade: Dict):
        # Get interval start using trunc function
        interval_start = self._ts_trunc(new_trade['time'])

        trade_price = float(new_trade['price'])
        trade_volume = float(new_trade['size'])
        #print(interval_start, trade_price, trade_volume)

                
        # Attempt to update an existing candle interval with this new trade
        try:
            # update low
            if trade_price < self.candle_data.at[interval_start, "low"]:
                self.candle_data.at[interval_start, "low"] = trade_price
            # update high
            if trade_price > self.candle_data.at[interval_start, "high"]:
                self.candle_data.at[interval_start, "high"] = trade_price
            # update close
            self.candle_data.at[interval_start, "close"] = trade_price
            # update volume
            self.candle_data.at[interval_start, "volume"] += trade_volume
        except KeyError as e:
            # KeyError here indicates a new interval has started that we do not have in the candle series
            # Do closing analysis on the last interval - compare to FTX historical feed-
            ftx_data = CandleSeries(self.market, self.resolution,2)
            latest_interval = self.get_latest_interval()
            ftx_interval = ftx_data.get_interval_data(latest_interval)
            internal_interval = self.get_interval_data(latest_interval)

            # Add variances onto the data in new cols
            self.candle_data.at[latest_interval, "open_var"] = internal_interval.open - ftx_interval.open 
            self.candle_data.at[latest_interval, "high_var"] = internal_interval.high - ftx_interval.high
            self.candle_data.at[latest_interval, "low_var"] = internal_interval.low - ftx_interval.low
            self.candle_data.at[latest_interval, "close_var"] = internal_interval.close - ftx_interval.close
            self.candle_data.at[latest_interval, "volume_var"] = internal_interval.volume - ftx_interval.volume

            # Get open interest
            self.candle_data.at[latest_interval, "open_interest"] = FTXClient.get_open_interest(self.market)

            # Create new candle interval with this trade
            new_candle_interval = {}
            new_candle_interval['open'] = self.candle_data.iloc[-1].close  #set open to close of the last interval
            new_candle_interval['high'] = trade_price  #set high to trade price
            new_candle_interval['low'] = trade_price  #set low to trade price
            new_candle_interval['close'] = trade_price  #set close to trade price
            new_candle_interval['volume'] = trade_volume  #set volume to trade volume

            # Append new row to the candle series data
            self.candle_data = self.candle_data.append(pd.DataFrame(new_candle_interval, index=[interval_start]))

            # Pritning
            logging.info(f"New interval beginning for {self.market} at {self.resolution}sec resolution. Last 5 candles with variances from FTX data:")
            print(self, end="\n\n")
            logging.info("Continuing to listen to Websocket. Press Ctrl+C or Ctrl+Z to stop this process and dump candle data to csv.\n")
        except Exception as e:
            raise e
        


        






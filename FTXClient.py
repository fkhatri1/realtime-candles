import requests
import json
import datetime
import pandas as pd
import logging
from typing import Dict

_ENDPOINT = "https://ftx.com/api"

# Exception thrown if API returns an error
class FTXRequestError(Exception):
    pass


# Static class used as namespace for functions which invoke the FTX APIs
class FTXClient():    
    # Function get_historical_ohlc
    # Inputs:
    #   market - name of the market
    #   resolution - candle window length - options: 15, 60, 300, 900, 3600, 14400, 86400, or any multiple of 86400 up to 30*86400
    #   n - number of periods history to fetch
    # Returns:
    #   pandas df of ohlc data with n periods ending current period, indexed by starttime of the window
    def get_historical_ohlc(market:str, resolution:int, n:int):
        url = f"{_ENDPOINT}/markets/{market}/candles"

        # Calculate start timestamp as now - (resolution seconds * n periods)
        now_dt = datetime.datetime.now()
        start_dt = now_dt - (pd.to_timedelta(f"{resolution}s") * n)

        # Convert start_dt to epoch time (number of seconds since 1/1/1970)
        start_epoch = (start_dt - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")

        # Setup params for get call
        params = {"resolution": resolution, "start_time": start_epoch}

        # Perform get call
        try:
            r = requests.get(url, params=params).json()
        except Exception as e:
            # TODO: Implement better error handling here
            logging.error("Some error occurred when attemping API request.")
            raise e
        else:
            # Check if call succeeded
            if r['success']:
                result = r['result']
            else:
                # Throw exception with error message from the API back to the caller
                logging.error("API did not accept request.")
                raise FTXRequestError(r['error'])

            # Create pd dataframe
            df = pd.DataFrame(result)

            # Drop time column - not used
            df = df.drop(["time"], axis=1)

            # Cast window start times to timestamp dtypes
            df['startTime'] = pd.to_datetime(df['startTime'], utc = True)
            df.set_index('startTime', inplace=True)

            return df

    # Function get_open_interest
    # Fetches open interest from FTX for given market
    # Inputs:
    #   market - name of the market
    # Returns:
    #   open interest
    def get_open_interest(market:str):
        url= f"{_ENDPOINT}/futures/{market}/stats"

        # Perform get call
        try:
            r = requests.get(url).json()
        except Exception as e:
            # TODO: Implement better error handling here
            logging.error("Some error occurred when attemping API request.")
            raise e
        else:
            # Check if call succeeded
            if r['success']:
                result = r['result']
            else:
                # Throw exception with error message from the API back to the caller
                logging.error("API did not accept request.")
                raise FTXRequestError(r['error'])

            return result['openInterest']





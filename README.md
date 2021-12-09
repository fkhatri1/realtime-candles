
# Part 1 - SQL Tables
SQL statements to create tables to house trade and OHLC historical data is contained in `part_1.sql`.

# realtime-candles
## Running the code
Run the code by running main.py from a terminal like `./main.py`, or with any Python interpreter like `python3 main.py`.
Sample output is provided in `sample_output.txt`.
Sample unit test output is provided in `sample_test_output.txt`.

### Dependencies
This assumes your environment has these modules installed:
1. websocket
2. websocket-client

## Exiting the process
Exit by sending signals SIGINT (Ctrl+C) or SIGTSTP (Ctrl+Z) while running. It will dump candle data to CSV in the same directory.

## Design notes
Below are high-level notes describing the components of this solution. Details are in comments within the code.

**Note** - The tables from Part 1 are not used by the realtime-candles solution. To avoid dependencies of standing up a database, realtime-candles runs everything in memory.

### CandleSeries
CandleSeries contains candle data for a given market for a given candle window length. All data is maintained by the process in Pandas dataframes.
This class provides functionality to update candle data with new trade information. It handles turning of candle windows and compares local data with FTX historical data. It also fetches open interest at the turn of intervals.

Note - Locally-calculated OHCL data matches closely with FTX historical data. Variances that do occur are mostly within 1%. Variances could be occurring because of missed messages from the Websocket. Locally-calculated volume is way off, however. I describe more on this in the Todos below. 

### FTXClient
This class provides wrappers for getting historical OHLC and open interest for any market from FTX.

### FTXWebsocket
This class provides a wrapper for subscribing to the trades channel from FTX. It could easily be expanded to accommodate other channels in the websocket. For simplicity, I have only tested it with trades.
Once it is started, it will run forever and send each received message to the function bound to `on_message`.

## Future enhancements, Todos
1. **Volume** - Locally calculated volume for candle windows is not matching FTX historical volume. CandleSeries is summing up volume of trades correctly, but it doesn't match.  It could be the FTX historical volume includes trades from other exchanges which the Websocket does not provide. Need more time to study and troubleshoot this.
2. **Unit testing** - In a production setting, I would write unit tests for each of the functions in the above classes using Pytest. I have implemented only one unit test, for `CandleSeries._ts_trunc`.
3. **Performance 1** - At the turn of intervals, the CandleSeries objects call FTX twice to get historical data for comparison and open interest. While it's doing that, it is not processing new trades from the websocket. I am not sure if trade data can be lost this way, or if the socket will just queue them in a reliable way. 
4. **Performance 2** - Using pandas dataframes is memory intensive and can be slow. If we are dealing with huge volume (1000's of trades per second), we would want to use a more lightweight data structure.
5. **Performance 3** - Separating the ingestion of trades and candle interval turning into two daemon processes makes more sense for this application, especially if volume is high. I did not implement this.
6. **Local data** - I am saving candle data only to CSVs. A more strategic solution would be to save to a database for future processing, such as the ones created in Part 1.
7. **Error handling** - I have implemented only primitive error handling. I did put in try/catch blocks which can be expanded to retry operations or otherwise handle exceptions.
8. **Stopping** - Since the Websocket application runs forever, I am stopping it using `SIGINT` and `SIGTSTP` signals. A more graceful way to start/stop the Websocket connection would be better.
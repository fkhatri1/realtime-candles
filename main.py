#!/usr/bin/env python3
from FTXWebsocket import FTXWebsocket
from CandleSeries import CandleSeries
import signal, sys, logging, time, json

def main():
    # Setup logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    # Instantiate day, hour and minute candle series
    candles = [CandleSeries('BTC-PERP', res, 5) for res in [60, 3600, 86400]]
    logging.info("Minute, Hour and Day candle series instantiated.")

    # Function sig_handler
    # Signal handler to gracefully exit after getting sigint or sigterm.
    # I have not implemented a strategic way to close the websocket and stop updating candles in memory.
    # This signal handler is a basic solution for this implementation.
    def sig_handler(sig, frame):
        logging.info("Received interrupt or terminate signal. Writing candle data to csv and shutting down.")
        for c in candles:
            # Allow time for CSVs to write before exit
            c.dump_to_csv()
        logging.info("Goodbye.")    
        sys.exit(0)

    # Bind sigint and sigterm to sig_handler
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTSTP, sig_handler)

    # Function handle_message
    # Handles incoming trades from the Websocket
    # Sends new trades to CandleSeries objects as updates
    def handle_message(ws, msg):
        msg_data = json.loads(msg)
        if msg_data['type'] == 'update':
            for trade in msg_data['data']:
                for c in candles:
                    c.update(trade)

    # Function on_close
    # Indicates closing of Websocket
    def on_close(ws, close_status_code, close_msg):
        logging.info("Closing Websocket")

    # Setup the ws conn
    ws = FTXWebsocket(channel="trades", market="BTC-PERP", on_message = handle_message, on_close = on_close)
    logging.info("Websocket subscription established, now listening and updating local data.")
    logging.info("Updates to candle data will be reported here as intervals turn.")
    logging.info("Press Ctrl+C or Ctrl+Z to stop this process and dump candle data to csv.")

    # Run the ws forever
    ws.run()

if __name__ == '__main__':
    main()
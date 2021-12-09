import websocket
import json
from types import FunctionType

_ENDPOINT = "wss://ftx.com/ws/"

# class FTXWebsocket
# Basic implementation which allows binding of functions to handle messages and closing of the ws
# Uses WebSocketApp from websocket-client package to make the connection and collect streaming data
# This implementation is limited to handle only one channel for one market for simplicity. Could be enhanced to accommodate more.
# Better solution would be to run this as a daemon and update local data in the background
class FTXWebsocket():
    def __init__(self, channel:str, market:str, on_message:FunctionType, on_close:FunctionType):
        self.channel = channel
        self.market = market
        self.ws = websocket.WebSocketApp("wss://ftx.com/ws/",
                            on_open = self._subscribe, 
                            on_message = on_message,
                            on_error = None,  #TODO: Implement some error handling here
                            on_close = on_close)

    # Function _subscribe
    # Will attempt to subscribe to a channel from the FTX Websocket
    # For this implementation, have not implemented any error handling
    def _subscribe(self, ws):
        ws.send(json.dumps({'op': 'subscribe', 'channel': self.channel, 'market': self.market}))

    # Function run
    # Will recieve data from the ws forever.
    # I have not implemented a good stop function.
    # User can stop the process by sending a SIGINT,  SIGINT will be caught and everything shutdown gracefully
    def run(self):
        self.ws.run_forever()
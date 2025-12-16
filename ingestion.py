import json
import threading
import pandas as pd
from websocket import WebSocketApp

class BinanceIngestor:
    def __init__(self, symbols):
        self.symbols = symbols
        self.data = {sym: [] for sym in symbols}

    def _on_message(self, ws, message, symbol):
        msg = json.loads(message)
        self.data[symbol].append({
            "time": pd.to_datetime(msg["T"], unit="ms"),
            "price": float(msg["p"]),
            "qty": float(msg["q"])
        })

        if len(self.data[symbol]) > 1000:
            self.data[symbol].pop(0)

    def _start_socket(self, symbol):
        ws = WebSocketApp(
            f"wss://fstream.binance.com/ws/{symbol.lower()}@trade",
            on_message=lambda ws, msg: self._on_message(ws, msg, symbol)
        )
        ws.run_forever()

    def start(self):
        for sym in self.symbols:
            thread = threading.Thread(
                target=self._start_socket,
                args=(sym,),
                daemon=True
            )
            thread.start()

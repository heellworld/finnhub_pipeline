import websocket
import json
import sys
import time
sys.path.append('..')
import finnhub_producer.config as config
from kafka import KafkaProducer

# Danh sách các công ty và mã chứng khoán tương ứng
COMPANIES = {
    "AAPL": "Apple",
    "META": "Facebook (Meta)",
    "GOOGL": "Google (Alphabet)",
    "AMZN": "Amazon"
}

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

class FinnhubClient:
    def __init__(self):
        self.ws = None

    def on_message(self, ws, message):
        data = json.loads(message)
        
        if 'data' in data:
            for item in data['data']:
                item['company'] = COMPANIES.get(item['s'], "Unknown")
            producer.send('finnhub_data', value=data)
            print(f"Sent: {data}")
        else:
            print(f"Received non-data message: {data}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"### closed ### {close_status_code} - {close_msg}")

    def on_open(self, ws):
        for symbol in COMPANIES.keys():
            ws.send(f'{{"type":"subscribe","symbol":"{symbol}"}}')
        print("Subscribed to all symbols")

    def connect(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={config.FINNHUB_API_KEY}",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

if __name__ == "__main__":
    client = FinnhubClient()
    client.connect()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        if client.ws:
            client.ws.close()
        print("Shutdown complete.")

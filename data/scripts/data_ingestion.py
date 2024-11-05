import websocket
import json
import os
import logging
import time
from datetime import datetime
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Configuration settings
CONFIG = {
    "market_data_url": "wss://marketdata.website.com/feed",
    "save_path": "/data/raw/tick_data/",
    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
    "max_retries": 5,
    "reconnect_delay": 10,
    "heartbeat_interval": 30,
    "data_validation": True,
    "file_rotation_size": 50 * 1024 * 1024,  # 50MB
}

# Ensure save path exists
if not os.path.exists(CONFIG['save_path']):
    os.makedirs(CONFIG['save_path'])

# Helper function to validate incoming data
def validate_data(data):
    required_fields = ['symbol', 'price', 'volume', 'timestamp']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Data validation failed. Missing field: {field}")
            return False
    return True

# Helper function to rotate data files based on file size
def rotate_file(symbol, file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) >= CONFIG['file_rotation_size']:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_file_path = file_path.replace('.json', f"_{timestamp}.json")
        os.rename(file_path, new_file_path)
        logger.info(f"Rotated file for {symbol} to {new_file_path}")
        return open(file_path, 'w')
    return open(file_path, 'a')

# WebSocket callback functions
def on_message(ws, message):
    try:
        data = json.loads(message)
        symbol = data.get('symbol')

        if symbol:
            if CONFIG['data_validation'] and not validate_data(data):
                return
            
            timestamp = datetime.now().strftime('%Y%m%d')
            file_path = os.path.join(CONFIG['save_path'], f"{symbol}_{timestamp}.json")
            
            with rotate_file(symbol, file_path) as file:
                json.dump(data, file)
                file.write("\n")
            logger.info(f"Data for {symbol} saved.")
        else:
            logger.warning("Received message without symbol data.")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def on_error(ws, error):
    logger.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")

def on_open(ws):
    logger.info("WebSocket connection opened")
    subscribe_message = {
        "type": "subscribe",
        "symbols": CONFIG['symbols']
    }
    ws.send(json.dumps(subscribe_message))
    logger.info(f"Subscribed to symbols: {CONFIG['symbols']}")

# Reconnect logic
def reconnect(ws, retries=0):
    if retries >= CONFIG['max_retries']:
        logger.error("Max retries reached. Exiting.")
        return
    
    logger.info(f"Reconnecting... Attempt {retries + 1}")
    time.sleep(CONFIG['reconnect_delay'])
    ws.run_forever()

# WebSocket client
def run_websocket():
    ws = websocket.WebSocketApp(CONFIG['market_data_url'],
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    try:
        ws.run_forever()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        reconnect(ws)

# Heartbeat to ensure connection is alive
def heartbeat(ws):
    while True:
        if ws.sock.connected:
            heartbeat_message = json.dumps({"type": "ping"})
            ws.send(heartbeat_message)
            logger.info("Sent heartbeat ping")
        else:
            logger.warning("WebSocket not connected.")
        time.sleep(CONFIG['heartbeat_interval'])

# Retry mechanism thread
def retry_mechanism():
    for i in range(CONFIG['max_retries']):
        logger.info(f"Retrying connection attempt {i + 1}")
        try:
            run_websocket()
            break
        except Exception as e:
            logger.error(f"Retry error: {e}")
            time.sleep(CONFIG['reconnect_delay'])

# Thread to handle heartbeat mechanism
def start_heartbeat_thread(ws):
    heartbeat_thread = Thread(target=heartbeat, args=(ws,))
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

# Function to start the data ingestion process
def start_data_ingestion():
    retry_thread = Thread(target=retry_mechanism)
    retry_thread.daemon = True
    retry_thread.start()
    
    logger.info("Started data ingestion process.")

if __name__ == "__main__":
    try:
        start_data_ingestion()
    except KeyboardInterrupt:
        logger.info("Data ingestion process interrupted.")
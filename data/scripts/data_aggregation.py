import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(filename='data_aggregation.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Path configurations for raw and processed data
RAW_TICK_DATA_PATH = 'data/raw/tick_data/'
RAW_ORDER_BOOK_DATA_PATH = 'data/raw/order_book_data/'
AGGREGATED_DATA_PATH = 'data/processed/aggregated_data/'

# Utility functions for VWAP and other metrics
def calculate_vwap(df):
    """Calculates VWAP (Volume Weighted Average Price) for tick data."""
    if df['volume'].sum() > 0:
        return (df['price'] * df['volume']).sum() / df['volume'].sum()
    return np.nan

def calculate_mid_price(df):
    """Calculates the mid-price for order book data."""
    return (df['best_bid'] + df['best_ask']) / 2

def calculate_spread(df):
    """Calculates the bid-ask spread for order book data."""
    return df['best_ask'] - df['best_bid']

# Aggregation functions for tick data
def aggregate_tick_data(df):
    """Aggregates tick data into OHLC bars and VWAP on a 1-minute basis."""
    df['vwap'] = df.resample('1T').apply(calculate_vwap)
    
    aggregated = df.resample('1T').agg({
        'price': ['ohlc'], # Open, High, Low, Close
        'volume': 'sum'
    })
    aggregated.columns = ['open', 'high', 'low', 'close', 'volume', 'vwap']
    return aggregated.dropna()

# Aggregation functions for order book data
def aggregate_order_book_data(df):
    """Aggregates order book data into OHLC bars for mid-price and volume data."""
    df['mid_price'] = df.resample('1T').apply(calculate_mid_price)
    df['spread'] = df.resample('1T').apply(calculate_spread)
    
    aggregated = df.resample('1T').agg({
        'mid_price': ['ohlc'], # Open, High, Low, Close of mid-price
        'bid_volume': 'sum',
        'ask_volume': 'sum',
        'spread': 'mean' # Average bid-ask spread over 1 minute
    })
    aggregated.columns = ['open', 'high', 'low', 'close', 'bid_volume', 'ask_volume', 'spread']
    return aggregated.dropna()

# Load raw CSV data and apply the appropriate aggregation function
def load_and_aggregate_data(file_path, aggregation_func):
    """Loads raw market data from CSV and aggregates using the provided function."""
    try:
        df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
        df.index = pd.to_datetime(df.index)
        return aggregation_func(df)
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return pd.DataFrame()

# Processing tick data
def process_tick_data():
    """Processes all tick data files and aggregates them."""
    logging.info("Starting tick data processing")
    aggregated_data = []
    for file in os.listdir(RAW_TICK_DATA_PATH):
        if file.endswith('.csv'):
            file_path = os.path.join(RAW_TICK_DATA_PATH, file)
            logging.info(f"Processing tick data file: {file_path}")
            aggregated = load_and_aggregate_data(file_path, aggregate_tick_data)
            if not aggregated.empty:
                aggregated_data.append(aggregated)
            else:
                logging.warning(f"No data aggregated from file: {file_path}")
    
    if aggregated_data:
        result = pd.concat(aggregated_data)
        result_file = os.path.join(AGGREGATED_DATA_PATH, f'aggregated_tick_data_{datetime.now().strftime("%Y%m%d")}.csv')
        result.to_csv(result_file)
        logging.info(f"Aggregated tick data saved to: {result_file}")
    else:
        logging.warning("No tick data files were aggregated.")

# Processing order book data
def process_order_book_data():
    """Processes all order book data files and aggregates them."""
    logging.info("Starting order book data processing")
    aggregated_data = []
    for file in os.listdir(RAW_ORDER_BOOK_DATA_PATH):
        if file.endswith('.csv'):
            file_path = os.path.join(RAW_ORDER_BOOK_DATA_PATH, file)
            logging.info(f"Processing order book data file: {file_path}")
            aggregated = load_and_aggregate_data(file_path, aggregate_order_book_data)
            if not aggregated.empty:
                aggregated_data.append(aggregated)
            else:
                logging.warning(f"No data aggregated from file: {file_path}")

    if aggregated_data:
        result = pd.concat(aggregated_data)
        result_file = os.path.join(AGGREGATED_DATA_PATH, f'aggregated_order_book_data_{datetime.now().strftime("%Y%m%d")}.csv')
        result.to_csv(result_file)
        logging.info(f"Aggregated order book data saved to: {result_file}")
    else:
        logging.warning("No order book data files were aggregated.")

# Utility function to ensure necessary directories exist
def ensure_directory_exists(directory):
    """Ensures that the given directory exists, creates it if not."""
    if not os.path.exists(directory):
        logging.info(f"Creating directory: {directory}")
        os.makedirs(directory)

# Main execution logic
if __name__ == '__main__':
    logging.info("Starting data aggregation process")

    # Ensure necessary directories exist
    ensure_directory_exists(AGGREGATED_DATA_PATH)

    # Process tick data
    process_tick_data()

    # Process order book data
    process_order_book_data()

    logging.info("Data aggregation process completed successfully")
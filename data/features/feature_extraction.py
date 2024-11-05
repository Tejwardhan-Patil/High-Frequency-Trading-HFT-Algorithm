import numpy as np
import pandas as pd
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volume import OnBalanceVolumeIndicator
from sklearn.preprocessing import StandardScaler

class FeatureExtractor:
    def __init__(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        
        required_columns = ['open', 'high', 'low', 'close', 'volume', 'bid_size', 'ask_size']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        self.data = data.copy()
        self.features = pd.DataFrame(index=self.data.index)

    def calculate_moving_averages(self, window_short=10, window_long=50):
        """Calculate short and long moving averages."""
        self.features['SMA_short'] = SMAIndicator(self.data['close'], window=window_short).sma_indicator()
        self.features['SMA_long'] = SMAIndicator(self.data['close'], window=window_long).sma_indicator()
        self.features['EMA'] = EMAIndicator(self.data['close'], window=window_long).ema_indicator()

    def calculate_macd(self, window_slow=26, window_fast=12, window_sign=9):
        """Calculate MACD (Moving Average Convergence Divergence)."""
        macd = MACD(self.data['close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
        self.features['MACD'] = macd.macd()
        self.features['MACD_signal'] = macd.macd_signal()
        self.features['MACD_diff'] = macd.macd_diff()

    def calculate_bollinger_bands(self, window=20, window_dev=2):
        """Calculate Bollinger Bands."""
        bb = BollingerBands(self.data['close'], window=window, window_dev=window_dev)
        self.features['BB_upper'] = bb.bollinger_hband()
        self.features['BB_lower'] = bb.bollinger_lband()
        self.features['BB_mavg'] = bb.bollinger_mavg()
        self.features['BB_bandwidth'] = bb.bollinger_wband()

    def calculate_rsi(self, window=14):
        """Calculate RSI (Relative Strength Index)."""
        rsi = RSIIndicator(self.data['close'], window=window)
        self.features['RSI'] = rsi.rsi()

    def calculate_stochastic_oscillator(self, window=14, smooth_window=3):
        """Calculate Stochastic Oscillator."""
        stoch = StochasticOscillator(self.data['high'], self.data['low'], self.data['close'], window=window, smooth_window=smooth_window)
        self.features['Stoch'] = stoch.stoch()

    def calculate_on_balance_volume(self):
        """Calculate On-Balance Volume."""
        obv = OnBalanceVolumeIndicator(self.data['close'], self.data['volume'])
        self.features['OBV'] = obv.on_balance_volume()

    def calculate_order_flow_imbalance(self):
        """Calculate order flow imbalance."""
        self.features['OFI'] = (self.data['bid_size'] - self.data['ask_size']) / (self.data['bid_size'] + self.data['ask_size'])

    def calculate_volatility(self, window=10):
        """Calculate rolling volatility."""
        self.features['Volatility'] = self.data['close'].rolling(window=window).std()

    def calculate_price_rate_of_change(self, window=12):
        """Calculate Price Rate of Change (ROC)."""
        self.features['Price_ROC'] = self.data['close'].pct_change(periods=window)

    def calculate_log_returns(self):
        """Calculate log returns of the close prices."""
        self.features['Log_Returns'] = np.log(self.data['close'] / self.data['close'].shift(1))

    def calculate_momentum(self, window=10):
        """Calculate Momentum indicator."""
        self.features['Momentum'] = self.data['close'] - self.data['close'].shift(window)

    def calculate_average_true_range(self, window=14):
        """Calculate Average True Range (ATR) to measure market volatility."""
        high_low = self.data['high'] - self.data['low']
        high_close = np.abs(self.data['high'] - self.data['close'].shift(1))
        low_close = np.abs(self.data['low'] - self.data['close'].shift(1))
        true_range = pd.DataFrame([high_low, high_close, low_close]).max(axis=0)
        self.features['ATR'] = true_range.rolling(window=window).mean()

    def add_time_features(self):
        """Add time-based features such as hour of the day and day of the week."""
        self.features['Hour'] = self.data.index.hour
        self.features['Day_of_Week'] = self.data.index.dayofweek

    def normalize_features(self):
        """Normalize feature values using StandardScaler."""
        scaler = StandardScaler()
        numeric_cols = self.features.select_dtypes(include=[np.number]).columns
        self.features[numeric_cols] = scaler.fit_transform(self.features[numeric_cols])

    def handle_missing_values(self):
        """Handle missing values by forward filling and backward filling."""
        self.features.fillna(method='ffill', inplace=True)
        self.features.fillna(method='bfill', inplace=True)

    def extract_features(self):
        """Extract all relevant features."""
        self.calculate_moving_averages()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        self.calculate_rsi()
        self.calculate_stochastic_oscillator()
        self.calculate_on_balance_volume()
        self.calculate_order_flow_imbalance()
        self.calculate_volatility()
        self.calculate_price_rate_of_change()
        self.calculate_log_returns()
        self.calculate_momentum()
        self.calculate_average_true_range()
        self.add_time_features()

        self.handle_missing_values()
        self.normalize_features()

        return self.features

# Usage:
# market_data = pd.read_csv('data/market_data.csv', parse_dates=True, index_col='timestamp')
# feature_extractor = FeatureExtractor(market_data)
# features = feature_extractor.extract_features()
# print(features.head())
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class MeanReversionStrategy:
    def __init__(self, window_size=20, z_score_threshold=2, capital=100000, stop_loss=None, take_profit=None):
        """
        Initializes the Mean Reversion Strategy.
        
        Parameters:
        - window_size: The lookback period for calculating the rolling mean and standard deviation.
        - z_score_threshold: The z-score at which buy/sell signals are generated.
        - capital: The starting capital for the strategy.
        - stop_loss: The stop loss level as a percentage of entry price.
        - take_profit: The take profit level as a percentage of entry price.
        """
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.capital = capital
        self.position = 0  # Current position in the market (long/short)
        self.entry_price = None  # Price at which the position was entered
        self.trade_log = []  # Store executed trades
        self.stop_loss = stop_loss  # Stop loss as percentage (e.g., 0.02 for 2%)
        self.take_profit = take_profit  # Take profit as percentage (e.g., 0.05 for 5%)

    def calculate_moving_average(self, prices):
        """
        Calculates the rolling moving average of the given price data.
        
        Parameters:
        - prices: A pandas Series of asset prices.
        
        Returns:
        - A pandas Series representing the moving average of the prices.
        """
        return prices.rolling(window=self.window_size).mean()

    def calculate_moving_std(self, prices):
        """
        Calculates the rolling standard deviation of the given price data.
        
        Parameters:
        - prices: A pandas Series of asset prices.
        
        Returns:
        - A pandas Series representing the rolling standard deviation of the prices.
        """
        return prices.rolling(window=self.window_size).std()

    def calculate_z_score(self, prices):
        """
        Calculates the z-score for the given price data relative to its rolling mean and standard deviation.
        
        Parameters:
        - prices: A pandas Series of asset prices.
        
        Returns:
        - A pandas Series representing the z-score for the prices.
        """
        rolling_mean = self.calculate_moving_average(prices)
        rolling_std = self.calculate_moving_std(prices)
        z_scores = (prices - rolling_mean) / rolling_std
        return z_scores

    def generate_signals(self, prices):
        """
        Generates buy and sell signals based on z-score deviations.
        
        Parameters:
        - prices: A pandas Series of asset prices.
        
        Returns:
        - A tuple of two pandas Series: buy_signals and sell_signals.
        """
        z_scores = self.calculate_z_score(prices)
        buy_signals = z_scores < -self.z_score_threshold
        sell_signals = z_scores > self.z_score_threshold
        return buy_signals, sell_signals

    def execute_trade(self, signal, price, timestamp):
        """
        Executes a trade based on the given signal (buy/sell) and updates the current position and capital.
        
        Parameters:
        - signal: A string indicating the trade signal ('buy' or 'sell').
        - price: The price at which the asset is being bought or sold.
        - timestamp: The time at which the trade is executed.
        """
        if signal == 'buy' and self.position == 0:
            # Enter long position
            self.position = self.capital / price
            self.entry_price = price
            self.trade_log.append((timestamp, 'buy', price))
        elif signal == 'sell' and self.position > 0:
            # Exit long position
            profit = (price - self.entry_price) * self.position
            self.capital += profit
            self.position = 0
            self.trade_log.append((timestamp, 'sell', price, profit))

    def apply_stop_loss_take_profit(self, price, timestamp):
        """
        Applies stop loss and take profit rules to automatically exit a position if criteria are met.
        
        Parameters:
        - price: The current market price.
        - timestamp: The current timestamp of the price data.
        """
        if self.position > 0:  # Check if there's an open position
            if self.stop_loss and price <= self.entry_price * (1 - self.stop_loss):
                self.execute_trade('sell', price, timestamp)
            elif self.take_profit and price >= self.entry_price * (1 + self.take_profit):
                self.execute_trade('sell', price, timestamp)

    def run_strategy(self, price_data):
        """
        Runs the mean reversion strategy on the provided price data.
        
        Parameters:
        - price_data: A pandas DataFrame containing historical price data with at least a 'Close' column.
        
        Returns:
        - A tuple of the trade log and the final capital after all trades.
        """
        buy_signals, sell_signals = self.generate_signals(price_data['Close'])
        for idx in range(len(price_data)):
            timestamp = price_data.index[idx]
            price = price_data['Close'][idx]
            
            # Check if any stop loss or take profit conditions are met
            self.apply_stop_loss_take_profit(price, timestamp)
            
            # Execute trades based on buy/sell signals
            if buy_signals[idx]:
                self.execute_trade('buy', price, timestamp)
            elif sell_signals[idx]:
                self.execute_trade('sell', price, timestamp)

        return self.trade_log, self.capital

if __name__ == "__main__":
    # Load historical market data from CSV
    data = pd.read_csv('market_data.csv', index_col='Date', parse_dates=True)
    
    # Define strategy parameters
    window_size = 20
    z_score_threshold = 2
    initial_capital = 100000
    stop_loss = 0.02  # 2% stop loss
    take_profit = 0.05  # 5% take profit
    
    # Initialize the strategy
    strategy = MeanReversionStrategy(window_size=window_size, z_score_threshold=z_score_threshold, 
                                     capital=initial_capital, stop_loss=stop_loss, take_profit=take_profit)
    
    # Run the strategy
    trade_log, final_capital = strategy.run_strategy(data)
    
    # Output the results
    print(f"Final Capital: {final_capital}")
    print(f"Total Trades Executed: {len(trade_log)}")
    
    # Print trade log
    for trade in trade_log:
        print(f"Trade: {trade}")

    # Detailed performance metrics calculation
    def calculate_performance_metrics(self):
        """
        Calculates detailed performance metrics for the strategy, such as 
        total return, Sharpe ratio, maximum drawdown, and more.
        
        Returns:
        - A dictionary containing performance metrics.
        """
        returns = []
        for i in range(1, len(self.trade_log)):
            _, action, price, *profit = self.trade_log[i]
            if action == 'sell':
                entry_timestamp, _, entry_price = self.trade_log[i-1]
                trade_return = (price - entry_price) / entry_price
                returns.append(trade_return)
        
        if len(returns) == 0:
            return {"Total Return": 0, "Sharpe Ratio": 0, "Max Drawdown": 0}

        # Calculate total return
        total_return = np.sum(returns)
        
        # Calculate Sharpe Ratio
        avg_return = np.mean(returns)
        return_std = np.std(returns)
        sharpe_ratio = avg_return / return_std if return_std != 0 else 0
        
        # Calculate Max Drawdown
        cumulative_returns = np.cumsum(returns)
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (peak - cumulative_returns) / peak
        max_drawdown = np.max(drawdown)
        
        return {
            "Total Return": total_return,
            "Sharpe Ratio": sharpe_ratio,
            "Max Drawdown": max_drawdown
        }

    # Function to generate a performance report
    def generate_performance_report(self):
        """
        Generates a performance report that includes all executed trades and performance metrics.
        
        Returns:
        - A string representation of the performance report.
        """
        report = []
        report.append(f"Performance Report for Mean Reversion Strategy")
        report.append(f"Final Capital: {self.capital}")
        report.append(f"Total Trades: {len(self.trade_log)}")
        
        # Append detailed trade log
        report.append("\nTrade Log:")
        for trade in self.trade_log:
            if len(trade) == 4:
                timestamp, action, price, profit = trade
                report.append(f"{timestamp}: {action.upper()} at {price}, Profit: {profit:.2f}")
            else:
                timestamp, action, price = trade
                report.append(f"{timestamp}: {action.upper()} at {price}")
        
        # Append performance metrics
        metrics = self.calculate_performance_metrics()
        report.append("\nPerformance Metrics:")
        report.append(f"Total Return: {metrics['Total Return']:.2f}")
        report.append(f"Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}")
        report.append(f"Max Drawdown: {metrics['Max Drawdown']:.2f}")
        
        return "\n".join(report)

    # Advanced logging system
    def log_trade(self, trade_details):
        """
        Logs trade details into an external log file for auditing and analysis.
        
        Parameters:
        - trade_details: A dictionary containing the trade information.
        """
        log_file = 'strategy_trade_log.txt'
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now()}: {trade_details}\n")
    
    # Incorporating moving average crossover confirmation for trade signals
    def moving_average_crossover_confirmation(self, prices):
        """
        Uses a dual moving average crossover strategy as confirmation for the 
        primary mean reversion signals. This prevents false signals and increases accuracy.
        
        Parameters:
        - prices: A pandas Series of asset prices.
        
        Returns:
        - A pandas Series representing a secondary confirmation signal.
        """
        short_window = self.window_size // 2
        long_window = self.window_size * 2
        short_mavg = prices.rolling(window=short_window).mean()
        long_mavg = prices.rolling(window=long_window).mean()

        crossover_signal = short_mavg > long_mavg
        return crossover_signal

    def run_advanced_strategy(self, price_data):
        """
        Runs the advanced version of the strategy with additional confirmation mechanisms and 
        enhanced risk management (e.g., stop-loss and take-profit).
        
        Parameters:
        - price_data: A pandas DataFrame containing historical price data with at least a 'Close' column.
        
        Returns:
        - A tuple of the trade log and the final capital after all trades.
        """
        buy_signals, sell_signals = self.generate_signals(price_data['Close'])
        crossover_signal = self.moving_average_crossover_confirmation(price_data['Close'])

        for idx in range(len(price_data)):
            timestamp = price_data.index[idx]
            price = price_data['Close'][idx]

            # Apply stop loss or take profit rules
            self.apply_stop_loss_take_profit(price, timestamp)
            
            # Check for buy/sell signals with crossover confirmation
            if buy_signals[idx] and crossover_signal[idx]:
                self.execute_trade('buy', price, timestamp)
                trade_details = {'action': 'buy', 'price': price, 'timestamp': timestamp}
                self.log_trade(trade_details)
            elif sell_signals[idx] and crossover_signal[idx]:
                self.execute_trade('sell', price, timestamp)
                trade_details = {'action': 'sell', 'price': price, 'timestamp': timestamp}
                self.log_trade(trade_details)

        return self.trade_log, self.capital

if __name__ == "__main__":
    # Load historical market data from CSV
    data = pd.read_csv('market_data.csv', index_col='Date', parse_dates=True)
    
    # Define strategy parameters
    window_size = 20
    z_score_threshold = 2
    initial_capital = 100000
    stop_loss = 0.02  # 2% stop loss
    take_profit = 0.05  # 5% take profit
    
    # Initialize the strategy
    strategy = MeanReversionStrategy(window_size=window_size, z_score_threshold=z_score_threshold, 
                                     capital=initial_capital, stop_loss=stop_loss, take_profit=take_profit)
    
    # Run the advanced version of the strategy with moving average crossover confirmation
    trade_log, final_capital = strategy.run_advanced_strategy(data)
    
    # Generate performance report
    performance_report = strategy.generate_performance_report()
    print(performance_report)
    
    # Print trade log
    for trade in trade_log:
        print(f"Trade: {trade}")
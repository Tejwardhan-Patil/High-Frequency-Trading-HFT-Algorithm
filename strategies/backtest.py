import pandas as pd
import numpy as np
from data.features.feature_extraction import extract_features
from analytics.performance_metrics import calculate_sharpe_ratio, calculate_drawdown
from utils.math_utils import calculate_volatility
from execution.risk_manager import enforce_risk_limits
import matplotlib.pyplot as plt
import logging
from utils.time_utils import format_timestamp
from execution.latency_monitor import LatencyMonitor
from risk_management.limits import PositionLimits, MaxLossLimit

class Backtest:
    def __init__(self, strategy, historical_data, initial_balance=1000000, transaction_cost=0.001):
        """
        Initialize the backtesting framework with the strategy, historical data, and initial parameters.
        Args:
            strategy: The trading strategy to be tested.
            historical_data: Historical market data used for backtesting.
            initial_balance: The starting capital for the backtest.
            transaction_cost: Transaction cost percentage (slippage, commission).
        """
        self.strategy = strategy
        self.historical_data = historical_data
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.cash_balance = initial_balance
        self.position = 0
        self.portfolio_value = initial_balance
        self.trades = []
        self.pnl_history = []
        self.equity_curve = []

    def run_backtest(self):
        """
        Execute the backtest by iterating over the historical data, generating trade signals, 
        executing trades, and updating portfolio value.
        """
        for index, row in self.historical_data.iterrows():
            # Extract features from the current row of data
            features = extract_features(row)
            
            # Generate a signal based on the strategy's logic
            signal = self.strategy.generate_signal(features)

            # Execute a buy or sell trade based on the signal
            if signal > 0 and self.position == 0:  # Buy signal
                self.execute_trade('buy', row['close'])
            elif signal < 0 and self.position > 0:  # Sell signal
                self.execute_trade('sell', row['close'])

            # Update the portfolio value based on the current price
            self.update_portfolio(row['close'])
            
            # Record profit and loss (PnL) history
            self.pnl_history.append(self.portfolio_value - self.initial_balance)
            
            # Track equity curve for performance evaluation
            self.equity_curve.append(self.portfolio_value)

        # Once the backtest is complete, evaluate the performance
        self.evaluate_performance()

    def execute_trade(self, trade_type, price):
        """
        Execute a trade by either buying or selling based on the trade type.
        Args:
            trade_type: 'buy' or 'sell' indicating the type of trade.
            price: The price at which the trade is executed.
        """
        if trade_type == 'buy':
            # Buy: Allocate the available cash to purchase as many units as possible
            self.position = self.cash_balance / price
            self.cash_balance = 0  # All cash is now allocated to the position
        elif trade_type == 'sell':
            # Sell: Liquidate the entire position and update the cash balance
            self.cash_balance = self.position * price
            self.position = 0  # No open position after selling

        # Record the executed trade with its details
        self.trades.append({'trade_type': trade_type, 'price': price})

    def update_portfolio(self, current_price):
        """
        Update the portfolio value by summing the current cash balance and the value of open positions.
        Args:
            current_price: The current price of the asset.
        """
        # Portfolio value is the sum of cash and the value of any open position
        self.portfolio_value = self.cash_balance + (self.position * current_price)

    def evaluate_performance(self):
        """
        Evaluate the performance of the backtest by calculating performance metrics.
        Metrics include Sharpe ratio, maximum drawdown, and portfolio volatility.
        """
        # Calculate key performance metrics using the PnL and equity curve data
        sharpe_ratio = calculate_sharpe_ratio(self.pnl_history)
        max_drawdown = calculate_drawdown(self.equity_curve)
        volatility = calculate_volatility(self.pnl_history)

        # Output performance metrics
        print(f"Sharpe Ratio: {sharpe_ratio}")
        print(f"Max Drawdown: {max_drawdown}")
        print(f"Volatility: {volatility}")

        # Plot the performance of the backtest for visualization
        self.plot_performance()

    def plot_performance(self):
        """
        Plot the equity curve for visual performance analysis of the backtest.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(self.equity_curve, label='Equity Curve')
        plt.title('Backtest Equity Curve')
        plt.xlabel('Time')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.show()


if __name__ == "__main__":
    # Load historical data for the backtest from a CSV file
    historical_data = pd.read_csv('data/processed/aggregated_data/minute_bars.csv')

    # Import and initialize a specific trading strategy for the backtest
    from strategies.mean_reversion.mean_reversion_strategy import MeanReversionStrategy
    strategy = MeanReversionStrategy()

    # Instantiate the Backtest class with the strategy and historical data
    backtester = Backtest(strategy, historical_data)

    # Run the backtest with the selected strategy and data
    backtester.run_backtest()

# Setting up logging for the backtest
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Backtest:
    def __init__(self, strategy, historical_data, initial_balance=1000000, transaction_cost=0.001):
        self.strategy = strategy
        self.historical_data = historical_data
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.cash_balance = initial_balance
        self.position = 0
        self.portfolio_value = initial_balance
        self.trades = []
        self.pnl_history = []
        self.equity_curve = []

        # Initialize risk management limits
        self.position_limits = PositionLimits(max_position_size=1000)
        self.max_loss_limit = MaxLossLimit(max_loss=50000)

        # Latency monitoring for the backtest
        self.latency_monitor = LatencyMonitor()

    def run_backtest(self):
        logger.info("Starting backtest with strategy: %s", self.strategy.__class__.__name__)

        # Main loop to process each historical data point
        for index, row in self.historical_data.iterrows():
            timestamp = format_timestamp(row['timestamp'])
            features = extract_features(row)

            # Start latency monitor for each iteration
            self.latency_monitor.start()

            # Generate trading signal
            signal = self.strategy.generate_signal(features)
            logger.debug("Generated signal: %s at time %s", signal, timestamp)

            # Risk checks before executing trade
            self.apply_risk_management(row['close'])

            if signal > 0 and self.position == 0:
                self.execute_trade('buy', row['close'])
            elif signal < 0 and self.position > 0:
                self.execute_trade('sell', row['close'])

            # Update portfolio after executing trade
            self.update_portfolio(row['close'])

            # Stop latency monitor and log time taken for this iteration
            self.latency_monitor.stop()
            logger.debug("Latency for iteration: %s ms", self.latency_monitor.get_latency())

            self.pnl_history.append(self.portfolio_value - self.initial_balance)
            self.equity_curve.append(self.portfolio_value)

            # Periodically log portfolio value
            if index % 100 == 0:
                logger.info("Portfolio value at %s: %s", timestamp, self.portfolio_value)

        self.evaluate_performance()

    def apply_risk_management(self, price):
        """
        Apply risk management checks such as position limits and maximum loss.
        """
        # Check position limits
        if not self.position_limits.check(self.position):
            logger.warning("Position size exceeds limit. Adjusting position size.")
            self.adjust_position(price)

        # Check maximum loss limits
        if not self.max_loss_limit.check(self.portfolio_value - self.initial_balance):
            logger.warning("Max loss limit reached. Liquidating position.")
            if self.position > 0:
                self.execute_trade('sell', price)

    def adjust_position(self, price):
        """
        Adjust the position size if it exceeds the risk limit.
        """
        if self.position > self.position_limits.max_position_size:
            excess_position = self.position - self.position_limits.max_position_size
            sell_amount = excess_position * price
            self.cash_balance += sell_amount
            self.position = self.position_limits.max_position_size
            logger.info("Reduced position size to fit within limit: %s units", self.position)

    def execute_trade(self, trade_type, price):
        super().execute_trade(trade_type, price)
        # Log trade details
        logger.info("Executed %s trade at price %s", trade_type, price)

    def evaluate_performance(self):
        logger.info("Evaluating backtest performance...")
        sharpe_ratio = calculate_sharpe_ratio(self.pnl_history)
        max_drawdown = calculate_drawdown(self.equity_curve)
        volatility = calculate_volatility(self.pnl_history)

        # Log performance metrics
        logger.info("Sharpe Ratio: %s", sharpe_ratio)
        logger.info("Max Drawdown: %s", max_drawdown)
        logger.info("Volatility: %s", volatility)

        self.plot_performance()

    def plot_performance(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve, label='Equity Curve')
        plt.title('Backtest Equity Curve with Strategy: ' + self.strategy.__class__.__name__)
        plt.xlabel('Time')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    # Load historical data
    logger.info("Loading historical data for backtesting...")
    historical_data = pd.read_csv('data/processed/aggregated_data/minute_bars.csv')

    # Strategy selection (Mean Reversion Strategy in this case)
    from strategies.mean_reversion.mean_reversion_strategy import MeanReversionStrategy
    strategy = MeanReversionStrategy()

    # Backtest initialization
    logger.info("Initializing backtest...")
    backtester = Backtest(strategy, historical_data)

    # Run the backtest
    backtester.run_backtest()

    logger.info("Backtest complete.")
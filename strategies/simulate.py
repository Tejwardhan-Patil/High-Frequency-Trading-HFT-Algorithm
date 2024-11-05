import pandas as pd
import numpy as np
from strategies.mean_reversion.mean_reversion_strategy import MeanReversionStrategy
from strategies.momentum.momentum_strategy import MomentumStrategy
from execution.order_manager import OrderManager
from risk_management.risk_manager import RiskManager
from analytics.performance_metrics import PerformanceMetrics
from utils.time_utils import get_current_time

# Load preprocessed market data (aggregated from raw data)
def load_market_data(data_path):
    """
    Load market data from CSV.
    The data should contain 'timestamp' and various market metrics.
    """
    return pd.read_csv(data_path, parse_dates=['timestamp'])

# Simulate trading for a specific strategy
class TradingSimulation:
    def __init__(self, strategy, initial_balance, risk_manager, order_manager, performance_metrics):
        """
        Initialize the trading simulation with the provided strategy, balance, risk management, and order execution setup.
        """
        self.strategy = strategy
        self.balance = initial_balance
        self.risk_manager = risk_manager
        self.order_manager = order_manager
        self.performance_metrics = performance_metrics
        self.positions = []  # To keep track of open positions
        self.trade_history = []  # Store executed trades

    def simulate(self, market_data):
        """
        Run the trading simulation on the provided market data.
        For each data point, apply the strategy and execute trades accordingly.
        """
        for index, row in market_data.iterrows():
            timestamp = row['timestamp']
            price_data = row.drop('timestamp')  # Extract price data excluding timestamp
            
            # Check risk before proceeding with a new trade decision
            if not self.risk_manager.check_risk_limits(self.positions, self.balance):
                print(f"Risk limits reached at {timestamp}. Exiting simulation.")
                break

            # Generate trade signals from the strategy
            signal = self.strategy.generate_signal(price_data)

            # Execute trades based on signals
            if signal == 'buy':
                trade = self.order_manager.execute_order('buy', price_data['close'])
                self.positions.append(trade)
                self.balance -= trade['cost']
            elif signal == 'sell' and self.positions:
                trade = self.order_manager.execute_order('sell', price_data['close'])
                self.positions.pop()
                self.balance += trade['revenue']

            # Store trade history
            self.trade_history.append({
                'timestamp': timestamp,
                'signal': signal,
                'balance': self.balance,
                'positions': len(self.positions)
            })

    def generate_report(self):
        """
        Generate a report of the simulation's performance metrics and return it.
        """
        return self.performance_metrics.calculate(self.trade_history)

# Main simulation function
def run_simulation(strategy_name, market_data_path, initial_balance=100000):
    """
    Execute a trading strategy simulation with the specified strategy and market data.
    """
    market_data = load_market_data(market_data_path)

    # Initialize risk manager, order manager, and performance metrics
    risk_manager = RiskManager(max_position_size=100, max_loss=0.2)
    order_manager = OrderManager()
    performance_metrics = PerformanceMetrics()

    # Select strategy based on the name provided
    if strategy_name == 'mean_reversion':
        strategy = MeanReversionStrategy()
    elif strategy_name == 'momentum':
        strategy = MomentumStrategy()
    else:
        raise ValueError("Unknown strategy name provided.")

    # Initialize the trading simulation
    simulation = TradingSimulation(strategy, initial_balance, risk_manager, order_manager, performance_metrics)

    # Run the simulation
    simulation.simulate(market_data)

    # Generate and print the performance report
    report = simulation.generate_report()
    print(report)

# Order Manager class handles order executions and their lifecycle
class OrderManager:
    def __init__(self):
        """
        Initialize the order manager to handle trade orders.
        """
        self.order_id_counter = 0

    def execute_order(self, order_type, price):
        """
        Execute a buy or sell order at the given price.
        """
        self.order_id_counter += 1
        if order_type == 'buy':
            return {
                'order_id': self.order_id_counter,
                'type': 'buy',
                'price': price,
                'cost': price * 100,  # Buying 100 units
                'timestamp': get_current_time()
            }
        elif order_type == 'sell':
            return {
                'order_id': self.order_id_counter,
                'type': 'sell',
                'price': price,
                'revenue': price * 100,  # Selling 100 units
                'timestamp': get_current_time()
            }
        else:
            raise ValueError(f"Unknown order type: {order_type}")

# Risk Manager class to handle risk limits and compliance
class RiskManager:
    def __init__(self, max_position_size, max_loss):
        """
        Initialize the risk manager with specified limits for position size and losses.
        """
        self.max_position_size = max_position_size
        self.max_loss = max_loss

    def check_risk_limits(self, positions, balance):
        """
        Check if current positions and balance are within risk limits.
        """
        if len(positions) > self.max_position_size:
            return False
        total_value_at_risk = sum([position['cost'] for position in positions])
        if total_value_at_risk / balance > self.max_loss:
            return False
        return True

# Performance Metrics class to handle calculation of key performance indicators
class PerformanceMetrics:
    def calculate(self, trade_history):
        """
        Calculate performance metrics based on the trade history.
        """
        # Calculate metrics like profit/loss, Sharpe ratio, etc
        total_profit = sum([trade['revenue'] - trade['cost'] for trade in trade_history if trade['signal'] == 'sell'])
        return {
            'total_profit': total_profit,
            'total_trades': len(trade_history),
        }

# Usage
if __name__ == "__main__":
    # Simulate a momentum strategy
    market_data_file = 'data/processed/aggregated_data/sample_market_data.csv'
    run_simulation('momentum', market_data_file)

# Advanced performance metrics to track risk-adjusted returns and drawdowns
class AdvancedPerformanceMetrics(PerformanceMetrics):
    def calculate(self, trade_history):
        """
        Calculate advanced performance metrics such as Sharpe ratio, drawdown, and volatility.
        """
        returns = self.calculate_returns(trade_history)
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        max_drawdown = self.calculate_max_drawdown(returns)
        volatility = self.calculate_volatility(returns)

        total_profit = sum([trade['revenue'] - trade['cost'] for trade in trade_history if trade['signal'] == 'sell'])
        
        return {
            'total_profit': total_profit,
            'total_trades': len(trade_history),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
        }

    def calculate_returns(self, trade_history):
        """
        Calculate returns based on the trade history. 
        Returns are computed as the change in balance after each trade.
        """
        returns = []
        previous_balance = trade_history[0]['balance']
        for trade in trade_history[1:]:
            current_balance = trade['balance']
            returns.append((current_balance - previous_balance) / previous_balance)
            previous_balance = current_balance
        return returns

    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.01):
        """
        Calculate the Sharpe Ratio, which is a measure of risk-adjusted return.
        """
        mean_return = np.mean(returns)
        return_std_dev = np.std(returns)
        sharpe_ratio = (mean_return - risk_free_rate) / return_std_dev if return_std_dev != 0 else 0
        return sharpe_ratio

    def calculate_max_drawdown(self, returns):
        """
        Calculate the maximum drawdown, which represents the largest peak-to-trough decline.
        """
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = running_max - cumulative_returns
        max_drawdown = np.max(drawdown)
        return max_drawdown

    def calculate_volatility(self, returns):
        """
        Calculate the volatility of the returns, representing the degree of variation.
        """
        return np.std(returns)

# Modified trading simulation class to use advanced metrics
class AdvancedTradingSimulation(TradingSimulation):
    def __init__(self, strategy, initial_balance, risk_manager, order_manager, performance_metrics):
        """
        Initialize the advanced trading simulation with advanced performance metrics.
        """
        super().__init__(strategy, initial_balance, risk_manager, order_manager, performance_metrics)

    def generate_report(self):
        """
        Generate a comprehensive report of the simulation, using advanced metrics.
        """
        return self.performance_metrics.calculate(self.trade_history)

# Simulate different strategies with risk management and advanced performance tracking
def run_advanced_simulation(strategy_name, market_data_path, initial_balance=100000):
    """
    Execute a trading strategy simulation with advanced performance metrics.
    """
    market_data = load_market_data(market_data_path)

    # Initialize risk manager, order manager, and advanced performance metrics
    risk_manager = RiskManager(max_position_size=100, max_loss=0.2)
    order_manager = OrderManager()
    performance_metrics = AdvancedPerformanceMetrics()

    # Select strategy based on the name provided
    if strategy_name == 'mean_reversion':
        strategy = MeanReversionStrategy()
    elif strategy_name == 'momentum':
        strategy = MomentumStrategy()
    else:
        raise ValueError("Unknown strategy name provided.")

    # Initialize the advanced trading simulation
    simulation = AdvancedTradingSimulation(strategy, initial_balance, risk_manager, order_manager, performance_metrics)

    # Run the simulation
    simulation.simulate(market_data)

    # Generate and print the performance report
    report = simulation.generate_report()
    print("\nAdvanced Performance Report:")
    for metric, value in report.items():
        print(f"{metric}: {value}")

# Custom logging for the simulation process
class SimulationLogger:
    def __init__(self, log_file):
        """
        Initialize the logger to write simulation logs to a file.
        """
        self.log_file = log_file
        with open(self.log_file, 'w') as f:
            f.write("Timestamp,Signal,Balance,Positions\n")

    def log_trade(self, timestamp, signal, balance, positions):
        """
        Log the details of each trade, including timestamp, signal, balance, and positions.
        """
        with open(self.log_file, 'a') as f:
            f.write(f"{timestamp},{signal},{balance},{positions}\n")

# Integrate logging into the advanced trading simulation
class LoggedTradingSimulation(AdvancedTradingSimulation):
    def __init__(self, strategy, initial_balance, risk_manager, order_manager, performance_metrics, logger):
        """
        Initialize the trading simulation with logging capabilities.
        """
        super().__init__(strategy, initial_balance, risk_manager, order_manager, performance_metrics)
        self.logger = logger

    def simulate(self, market_data):
        """
        Run the trading simulation and log every trade.
        """
        for index, row in market_data.iterrows():
            timestamp = row['timestamp']
            price_data = row.drop('timestamp')  # Extract price data excluding timestamp
            
            # Check risk before proceeding with a new trade decision
            if not self.risk_manager.check_risk_limits(self.positions, self.balance):
                print(f"Risk limits reached at {timestamp}. Exiting simulation.")
                break

            # Generate trade signals from the strategy
            signal = self.strategy.generate_signal(price_data)

            # Execute trades based on signals
            if signal == 'buy':
                trade = self.order_manager.execute_order('buy', price_data['close'])
                self.positions.append(trade)
                self.balance -= trade['cost']
            elif signal == 'sell' and self.positions:
                trade = self.order_manager.execute_order('sell', price_data['close'])
                self.positions.pop()
                self.balance += trade['revenue']

            # Log the trade details
            self.logger.log_trade(timestamp, signal, self.balance, len(self.positions))

            # Store trade history
            self.trade_history.append({
                'timestamp': timestamp,
                'signal': signal,
                'balance': self.balance,
                'positions': len(self.positions)
            })

# Usage for advanced simulation with logging
if __name__ == "__main__":
    # Define the path to the market data file
    market_data_file = 'data/processed/aggregated_data/sample_market_data.csv'

    # Create a logger to log simulation details
    logger = SimulationLogger('simulation_log.csv')

    # Run an advanced simulation with logging
    logged_simulation = LoggedTradingSimulation(
        strategy=MomentumStrategy(),
        initial_balance=100000,
        risk_manager=RiskManager(max_position_size=100, max_loss=0.2),
        order_manager=OrderManager(),
        performance_metrics=AdvancedPerformanceMetrics(),
        logger=logger
    )

    # Load market data and run the simulation
    market_data = load_market_data(market_data_file)
    logged_simulation.simulate(market_data)

    # Generate and print the performance report
    report = logged_simulation.generate_report()
    print("\nFinal Performance Report:")
    for metric, value in report.items():
        print(f"{metric}: {value}")
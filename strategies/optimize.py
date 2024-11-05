import numpy as np
import pandas as pd
from sklearn.model_selection import ParameterGrid
from bayes_opt import BayesianOptimization
from strategies.backtest import backtest_strategy  
from strategies.simulate import simulate_strategy  

# Optimization Class for Strategy Parameter Tuning
class StrategyOptimizer:
    def __init__(self, strategy, data, param_grid):
        """
        Initialize the optimizer with the given strategy, historical data, and parameter grid.

        Parameters:
        strategy (str): Name of the strategy to optimize.
        data (pd.DataFrame): Historical data to use for backtesting.
        param_grid (dict): Dictionary defining the grid of parameters to search.
        """
        self.strategy = strategy
        self.data = data
        self.param_grid = param_grid
    
    def evaluate_strategy(self, **params):
        """
        Backtest the strategy with a given set of parameters and return the performance metric.

        Parameters:
        **params: Arbitrary keyword arguments representing strategy parameters.

        Returns:
        float: The performance metric of the backtested strategy.
        """
        result = backtest_strategy(self.strategy, self.data, **params)
        return result['performance_metric']  # backtest_strategy returns a dictionary with performance metrics

    def optimize_grid_search(self):
        """
        Optimize strategy parameters using grid search.

        Returns:
        tuple: Best parameters and the corresponding best performance score.
        """
        best_score = -np.inf
        best_params = None
        for params in ParameterGrid(self.param_grid):
            print(f"Evaluating parameters: {params}")  # Track evaluation progress
            score = self.evaluate_strategy(**params)
            print(f"Performance Score: {score}")
            if score > best_score:
                best_score = score
                best_params = params
                print(f"New best score: {best_score} with parameters: {best_params}")
        return best_params, best_score

    def optimize_bayesian(self, bounds):
        """
        Optimize strategy parameters using Bayesian optimization.

        Parameters:
        bounds (dict): Bounds for each parameter to be optimized.

        Returns:
        dict: The best parameters and the corresponding best performance score.
        """
        def black_box_function(**params):
            return self.evaluate_strategy(**params)

        optimizer = BayesianOptimization(
            f=black_box_function,
            pbounds=bounds,
            random_state=1,
        )
        optimizer.maximize(init_points=5, n_iter=25)

        best_params = optimizer.max['params']
        best_score = optimizer.max['target']
        print(f"Best Bayesian Parameters: {best_params} with Score: {best_score}")
        return best_params, best_score

# Usage for a Mean Reversion Strategy
if __name__ == "__main__":
    # Load preprocessed historical data
    historical_data = pd.read_csv('/mnt/data/processed/aggregated_data/mean_reversion_data.csv')

    # Define parameter grid for grid search optimization
    param_grid = {
        'lookback_period': [5, 10, 15, 20],
        'entry_threshold': [0.01, 0.02, 0.03],
        'exit_threshold': [0.01, 0.02, 0.03],
    }

    # Define bounds for Bayesian Optimization
    bayesian_bounds = {
        'lookback_period': (5, 20),
        'entry_threshold': (0.01, 0.05),
        'exit_threshold': (0.01, 0.05),
    }

    # Initialize optimizer for the mean reversion strategy
    optimizer = StrategyOptimizer(strategy='mean_reversion', data=historical_data, param_grid=param_grid)

    # Optimize using grid search
    print("Starting Grid Search Optimization...")
    best_params_grid, best_score_grid = optimizer.optimize_grid_search()
    print(f"Best Parameters (Grid Search): {best_params_grid}, Best Score: {best_score_grid}")

    # Prepare for Bayesian Optimization
    print("Starting Bayesian Optimization...")
    best_params_bayes, best_score_bayes = optimizer.optimize_bayesian(bounds=bayesian_bounds)
    print(f"Best Parameters (Bayesian Optimization): {best_params_bayes}, Best Score: {best_score_bayes}")

# Additional function for simulating the strategy with optimized parameters
def simulate_with_best_params(optimizer, strategy, param_grid, bounds, data):
    """
    Simulate the strategy using the best parameters from both optimization methods.
    
    Parameters:
    optimizer (StrategyOptimizer): Initialized optimizer object.
    strategy (str): Name of the strategy to simulate.
    param_grid (dict): Parameter grid for grid search.
    bounds (dict): Parameter bounds for Bayesian optimization.
    data (pd.DataFrame): Historical data for the simulation.

    Returns:
    None
    """
    # Grid Search Best Parameters
    print("Simulating with Grid Search Best Parameters...")
    best_params_grid, best_score_grid = optimizer.optimize_grid_search()
    simulation_result_grid = simulate_strategy(strategy, data, **best_params_grid)
    print(f"Simulation Result (Grid Search): {simulation_result_grid}")

    # Bayesian Optimization Best Parameters
    print("Simulating with Bayesian Optimization Best Parameters...")
    best_params_bayes, best_score_bayes = optimizer.optimize_bayesian(bounds=bounds)
    simulation_result_bayes = simulate_strategy(strategy, data, **best_params_bayes)
    print(f"Simulation Result (Bayesian Optimization): {simulation_result_bayes}")

# Function to display results and performance metrics
def display_results(simulation_results):
    """
    Display the performance metrics of the strategy after the simulation.

    Parameters:
    simulation_results (dict): A dictionary containing the simulation results and performance metrics.

    Returns:
    None
    """
    print("\nSimulation Performance Metrics:")
    for metric, value in simulation_results.items():
        print(f"{metric}: {value}")

# Function for logging the optimization process
def log_optimization_results(log_file, params, score, method):
    """
    Log the results of the optimization process to a file.

    Parameters:
    log_file (str): Path to the log file.
    params (dict): The best parameters from the optimization process.
    score (float): The performance score of the strategy.
    method (str): The optimization method used (e.g., 'grid_search', 'bayesian').

    Returns:
    None
    """
    with open(log_file, 'a') as f:
        f.write(f"Optimization Method: {method}\n")
        f.write(f"Best Parameters: {params}\n")
        f.write(f"Best Score: {score}\n\n")
    print(f"Results logged to {log_file}")

# Full optimization process including both methods and simulation
def full_optimization_process(strategy, data, param_grid, bounds, log_file):
    """
    Run the full optimization process using grid search, Bayesian optimization, 
    and then simulate with the best parameters.

    Parameters:
    strategy (str): The strategy to optimize.
    data (pd.DataFrame): Historical data for backtesting and simulation.
    param_grid (dict): Parameter grid for grid search.
    bounds (dict): Parameter bounds for Bayesian optimization.
    log_file (str): Path to the file where results will be logged.

    Returns:
    None
    """
    optimizer = StrategyOptimizer(strategy=strategy, data=data, param_grid=param_grid)

    # Run Grid Search Optimization
    print("\n===== Grid Search Optimization =====")
    best_params_grid, best_score_grid = optimizer.optimize_grid_search()
    print(f"Grid Search - Best Parameters: {best_params_grid}, Best Score: {best_score_grid}")
    log_optimization_results(log_file, best_params_grid, best_score_grid, 'grid_search')

    # Simulate with Grid Search best parameters
    print("\nSimulating with Grid Search best parameters...")
    simulation_result_grid = simulate_strategy(strategy, data, **best_params_grid)
    display_results(simulation_result_grid)

    # Run Bayesian Optimization
    print("\n===== Bayesian Optimization =====")
    best_params_bayes, best_score_bayes = optimizer.optimize_bayesian(bounds)
    print(f"Bayesian Optimization - Best Parameters: {best_params_bayes}, Best Score: {best_score_bayes}")
    log_optimization_results(log_file, best_params_bayes, best_score_bayes, 'bayesian')

    # Simulate with Bayesian Optimization best parameters
    print("\nSimulating with Bayesian best parameters...")
    simulation_result_bayes = simulate_strategy(strategy, data, **best_params_bayes)
    display_results(simulation_result_bayes)

# Helper function to load data for multiple strategies
def load_data_for_strategy(strategy_name):
    """
    Load the appropriate data for the specified strategy.

    Parameters:
    strategy_name (str): The name of the strategy for which data should be loaded.

    Returns:
    pd.DataFrame: The historical data for the strategy.
    """
    if strategy_name == 'mean_reversion':
        return pd.read_csv('/mnt/data/processed/aggregated_data/mean_reversion_data.csv')
    elif strategy_name == 'momentum':
        return pd.read_csv('/mnt/data/processed/aggregated_data/momentum_data.csv')
    elif strategy_name == 'arbitrage':
        return pd.read_csv('/mnt/data/processed/aggregated_data/arbitrage_data.csv')
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

# Usage for running the full optimization process
if __name__ == "__main__":
    # Define the strategy to optimize
    strategy = 'mean_reversion'

    # Load historical data for the strategy
    historical_data = load_data_for_strategy(strategy)

    # Parameter grid for grid search
    param_grid = {
        'lookback_period': [5, 10, 15, 20],
        'entry_threshold': [0.01, 0.02, 0.03],
        'exit_threshold': [0.01, 0.02, 0.03],
    }

    # Bounds for Bayesian optimization
    bayesian_bounds = {
        'lookback_period': (5, 20),
        'entry_threshold': (0.01, 0.05),
        'exit_threshold': (0.01, 0.05),
    }

    # Path to the log file
    log_file = '/mnt/data/optimization_logs.txt'

    # Run the full optimization process
    full_optimization_process(strategy, historical_data, param_grid, bayesian_bounds, log_file)

# Additional strategy optimizations for other strategies
def optimize_momentum_strategy():
    """
    Optimize and simulate the momentum strategy using both optimization methods.

    Returns:
    None
    """
    strategy = 'momentum'
    data = load_data_for_strategy(strategy)

    param_grid = {
        'momentum_window': [10, 20, 30],
        'signal_strength': [0.05, 0.1, 0.15],
        'exit_threshold': [0.01, 0.02, 0.03],
    }

    bayesian_bounds = {
        'momentum_window': (10, 30),
        'signal_strength': (0.05, 0.2),
        'exit_threshold': (0.01, 0.05),
    }

    log_file = '/mnt/data/optimization_logs_momentum.txt'

    full_optimization_process(strategy, data, param_grid, bayesian_bounds, log_file)

def optimize_arbitrage_strategy():
    """
    Optimize and simulate the arbitrage strategy using both optimization methods.

    Returns:
    None
    """
    strategy = 'arbitrage'
    data = load_data_for_strategy(strategy)

    param_grid = {
        'price_spread_threshold': [0.01, 0.02, 0.03],
        'max_position_size': [10, 20, 30],
        'entry_delay': [0, 1, 2],
    }

    bayesian_bounds = {
        'price_spread_threshold': (0.01, 0.05),
        'max_position_size': (10, 40),
        'entry_delay': (0, 3),
    }

    log_file = '/mnt/data/optimization_logs_arbitrage.txt'

    full_optimization_process(strategy, data, param_grid, bayesian_bounds, log_file)

# Running additional optimizations
if __name__ == "__main__":
    # Run momentum strategy optimization
    print("\nOptimizing Momentum Strategy...")
    optimize_momentum_strategy()

    # Run arbitrage strategy optimization
    print("\nOptimizing Arbitrage Strategy...")
    optimize_arbitrage_strategy()
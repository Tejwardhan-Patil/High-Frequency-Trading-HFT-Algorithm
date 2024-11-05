import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculate the Sharpe ratio for the given strategy returns.

    Parameters:
    - returns: Pandas Series of strategy returns.
    - risk_free_rate: Risk-free rate for Sharpe ratio calculation.

    Returns:
    - Sharpe ratio
    """
    if returns.empty:
        return np.nan
    excess_returns = returns - risk_free_rate
    mean_excess_return = np.mean(excess_returns)
    volatility = np.std(excess_returns)
    
    if volatility == 0:
        return np.nan  # No variation in returns

    return mean_excess_return / volatility

def calculate_drawdown(equity_curve):
    """
    Calculate the maximum drawdown for the given equity curve.

    Parameters:
    - equity_curve: Pandas Series of equity values.

    Returns:
    - max_drawdown: Maximum drawdown
    - drawdown_duration: Duration of the drawdown
    """
    if equity_curve.empty:
        return np.nan, np.nan
    
    drawdowns = equity_curve / equity_curve.cummax() - 1
    max_drawdown = drawdowns.min()

    if max_drawdown == 0:
        return 0, 0  # No drawdown observed
    
    # Calculate drawdown duration (time until recovery)
    end_of_drawdown = np.argmax(drawdowns == max_drawdown)
    start_of_recovery = (drawdowns[end_of_drawdown:] == 0).idxmax()

    drawdown_duration = start_of_recovery - end_of_drawdown
    
    return max_drawdown, drawdown_duration

def calculate_slippage(execution_prices, market_prices):
    """
    Calculate slippage, the difference between execution price and market price.

    Parameters:
    - execution_prices: Pandas Series of the prices at which trades were executed.
    - market_prices: Pandas Series of the corresponding market prices.

    Returns:
    - Slippage as a float.
    """
    if execution_prices.empty or market_prices.empty:
        return np.nan
    
    if len(execution_prices) != len(market_prices):
        raise ValueError("Execution and market prices must have the same length.")

    slippage = execution_prices - market_prices
    return np.mean(slippage)

def calculate_volatility(returns, window=252):
    """
    Calculate annualized volatility of returns.

    Parameters:
    - returns: Pandas Series of daily returns.
    - window: Window size for annualization (252 for daily returns).

    Returns:
    - Volatility as a float.
    """
    if returns.empty:
        return np.nan
    
    daily_volatility = np.std(returns)
    annualized_volatility = daily_volatility * np.sqrt(window)

    return annualized_volatility

def calculate_sortino_ratio(returns, risk_free_rate=0.0):
    """
    Calculate the Sortino ratio.

    Parameters:
    - returns: Pandas Series of strategy returns.
    - risk_free_rate: Risk-free rate for Sortino ratio calculation.

    Returns:
    - Sortino ratio
    """
    if returns.empty:
        return np.nan
    
    downside_returns = returns[returns < risk_free_rate]
    downside_risk = np.std(downside_returns)

    if downside_risk == 0:
        return np.nan  # No downside risk

    return np.mean(returns - risk_free_rate) / downside_risk

def calculate_win_loss_ratio(trades):
    """
    Calculate the win/loss ratio of a series of trades.

    Parameters:
    - trades: Pandas Series of trade returns (positive for wins, negative for losses).

    Returns:
    - win_loss_ratio: Ratio of winning trades to losing trades.
    """
    wins = trades[trades > 0]
    losses = trades[trades < 0]
    
    if len(losses) == 0:
        return np.inf  # No losses, perfect win ratio

    return len(wins) / len(losses)

def calculate_profit_factor(trades):
    """
    Calculate the profit factor, the ratio of gross profits to gross losses.

    Parameters:
    - trades: Pandas Series of trade returns.

    Returns:
    - profit_factor: Ratio of gross profits to gross losses.
    """
    gross_profit = trades[trades > 0].sum()
    gross_loss = trades[trades < 0].sum()

    if gross_loss == 0:
        return np.inf  # No losses, perfect profit factor

    return gross_profit / abs(gross_loss)

def calculate_trade_expectancy(trades):
    """
    Calculate trade expectancy, the average amount won or lost per trade.

    Parameters:
    - trades: Pandas Series of trade returns.

    Returns:
    - expectancy: The expected value of each trade.
    """
    if trades.empty:
        return np.nan
    
    return np.mean(trades)

def calculate_average_trade_duration(trade_durations):
    """
    Calculate the average duration of trades.

    Parameters:
    - trade_durations: Pandas Series of trade durations in time units.

    Returns:
    - average_duration: The average trade duration.
    """
    if trade_durations.empty:
        return np.nan
    
    return np.mean(trade_durations)

def calculate_max_consecutive_wins_losses(trades):
    """
    Calculate the maximum number of consecutive wins and losses.

    Parameters:
    - trades: Pandas Series of trade returns.

    Returns:
    - max_consecutive_wins: Maximum consecutive winning trades.
    - max_consecutive_losses: Maximum consecutive losing trades.
    """
    consecutive_wins = (trades > 0).astype(int).groupby((trades > 0).ne((trades > 0).shift()).cumsum()).cumsum()
    consecutive_losses = (trades < 0).astype(int).groupby((trades < 0).ne((trades < 0).shift()).cumsum()).cumsum()

    max_consecutive_wins = consecutive_wins.max()
    max_consecutive_losses = consecutive_losses.max()

    return max_consecutive_wins, max_consecutive_losses

def performance_summary(equity_curve, returns, trades=None, trade_durations=None, execution_prices=None, market_prices=None):
    """
    Generate a performance summary including key metrics like Sharpe ratio, drawdown, slippage, and other advanced metrics.

    Parameters:
    - equity_curve: Pandas Series of the equity curve.
    - returns: Pandas Series of strategy returns.
    - trades: (Optional) Pandas Series of individual trade returns for additional metrics.
    - trade_durations: (Optional) Pandas Series of trade durations.
    - execution_prices: (Optional) Pandas Series of execution prices for slippage calculation.
    - market_prices: (Optional) Pandas Series of market prices for slippage calculation.

    Returns:
    - Dictionary containing performance metrics.
    """
    metrics = {}
    
    metrics['sharpe_ratio'] = calculate_sharpe_ratio(returns)
    metrics['max_drawdown'], metrics['drawdown_duration'] = calculate_drawdown(equity_curve)
    metrics['volatility'] = calculate_volatility(returns)
    metrics['sortino_ratio'] = calculate_sortino_ratio(returns)
    
    if trades is not None:
        metrics['win_loss_ratio'] = calculate_win_loss_ratio(trades)
        metrics['profit_factor'] = calculate_profit_factor(trades)
        metrics['trade_expectancy'] = calculate_trade_expectancy(trades)
        metrics['max_consecutive_wins'], metrics['max_consecutive_losses'] = calculate_max_consecutive_wins_losses(trades)
    
    if trade_durations is not None:
        metrics['average_trade_duration'] = calculate_average_trade_duration(trade_durations)

    if execution_prices is not None and market_prices is not None:
        metrics['slippage'] = calculate_slippage(execution_prices, market_prices)

    return metrics
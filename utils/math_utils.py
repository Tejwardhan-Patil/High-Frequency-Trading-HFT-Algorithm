import numpy as np

def simple_moving_average(data, window_size):
    """
    Calculate Simple Moving Average (SMA) for the given data.

    :param data: Array or list of price data.
    :param window_size: Number of periods for the moving average.
    :return: Array of SMA values.
    """
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def exponential_moving_average(data, window_size):
    """
    Calculate Exponential Moving Average (EMA) for the given data.

    :param data: Array or list of price data.
    :param window_size: Number of periods for the moving average.
    :return: Array of EMA values.
    """
    alpha = 2 / (window_size + 1)
    ema = np.zeros(len(data))
    ema[0] = data[0]
    for i in range(1, len(data)):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
    return ema

def weighted_moving_average(data, weights):
    """
    Calculate Weighted Moving Average (WMA) for the given data.

    :param data: Array or list of price data.
    :param weights: Array or list of weights for the moving average.
    :return: Weighted moving average.
    """
    weights = np.array(weights)
    return np.convolve(data, weights / weights.sum(), mode='valid')

def volatility(data, window_size):
    """
    Calculate the volatility (standard deviation) for the given data.

    :param data: Array or list of price data.
    :param window_size: Number of periods for volatility calculation.
    :return: Array of volatility values.
    """
    return np.std([data[i:i + window_size] for i in range(len(data) - window_size + 1)], axis=1)

def rolling_max(data, window_size):
    """
    Calculate the rolling maximum value over a specified window.

    :param data: Array or list of price data.
    :param window_size: Size of the rolling window.
    :return: Array of rolling max values.
    """
    return np.array([np.max(data[i:i + window_size]) for i in range(len(data) - window_size + 1)])

def rolling_min(data, window_size):
    """
    Calculate the rolling minimum value over a specified window.

    :param data: Array or list of price data.
    :param window_size: Size of the rolling window.
    :return: Array of rolling min values.
    """
    return np.array([np.min(data[i:i + window_size]) for i in range(len(data) - window_size + 1)])

def relative_strength_index(data, window_size=14):
    """
    Calculate Relative Strength Index (RSI).

    :param data: Array or list of price data.
    :param window_size: Number of periods for RSI calculation.
    :return: Array of RSI values.
    """
    delta = np.diff(data)
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)

    avg_gain = np.convolve(gains, np.ones(window_size) / window_size, mode='valid')
    avg_loss = np.convolve(losses, np.ones(window_size) / window_size, mode='valid')

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return np.concatenate([np.full(window_size, np.nan), rsi])

def calculate_vwap(prices, volumes):
    """
    Calculate the Volume-Weighted Average Price (VWAP).

    :param prices: Array or list of price data.
    :param volumes: Array or list of volume data corresponding to the prices.
    :return: VWAP value.
    """
    return np.sum(prices * volumes) / np.sum(volumes)

def calculate_z_score(data, window_size):
    """
    Calculate Z-score for mean reversion strategies.

    :param data: Array or list of price data.
    :param window_size: Size of the rolling window for mean and standard deviation.
    :return: Array of Z-score values.
    """
    rolling_mean = simple_moving_average(data, window_size)
    rolling_std = np.std([data[i:i + window_size] for i in range(len(data) - window_size + 1)], axis=1)
    return (data[window_size - 1:] - rolling_mean) / rolling_std

def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """
    Calculate the Sharpe Ratio.

    :param returns: Array or list of return values.
    :param risk_free_rate: The risk-free rate for Sharpe ratio calculation.
    :return: Sharpe ratio value.
    """
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns)

def drawdown(returns):
    """
    Calculate drawdown from a series of returns.

    :param returns: Array or list of return values.
    :return: Array of drawdown values.
    """
    cumulative_returns = np.cumsum(returns)
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = cumulative_returns - peak
    return drawdown

def max_drawdown(returns):
    """
    Calculate the maximum drawdown from a series of returns.

    :param returns: Array or list of return values.
    :return: Maximum drawdown value.
    """
    cumulative_returns = np.cumsum(returns)
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = cumulative_returns - peak
    return np.min(drawdown)

def rolling_mean(data, window_size):
    """
    Calculate rolling mean over a specified window size.

    :param data: Array or list of price data.
    :param window_size: Size of the rolling window.
    :return: Array of rolling mean values.
    """
    return np.array([np.mean(data[i:i + window_size]) for i in range(len(data) - window_size + 1)])

def price_diff(data):
    """
    Calculate the price difference between consecutive data points.

    :param data: Array or list of price data.
    :return: Array of price differences.
    """
    return np.diff(data)

def cumulative_returns(returns):
    """
    Calculate the cumulative returns from a series of returns.

    :param returns: Array or list of return values.
    :return: Array of cumulative returns.
    """
    return np.cumsum(returns)

def beta(returns, benchmark_returns):
    """
    Calculate the beta of a series of returns relative to a benchmark.

    :param returns: Array or list of asset returns.
    :param benchmark_returns: Array or list of benchmark returns.
    :return: Beta value.
    """
    covariance_matrix = np.cov(returns, benchmark_returns)
    return covariance_matrix[0, 1] / covariance_matrix[1, 1]

def alpha(returns, benchmark_returns, risk_free_rate=0):
    """
    Calculate the alpha of a series of returns relative to a benchmark.

    :param returns: Array or list of asset returns.
    :param benchmark_returns: Array or list of benchmark returns.
    :param risk_free_rate: The risk-free rate for calculating alpha.
    :return: Alpha value.
    """
    excess_returns = returns - risk_free_rate
    benchmark_excess_returns = benchmark_returns - risk_free_rate
    beta_value = beta(excess_returns, benchmark_excess_returns)
    return np.mean(excess_returns) - beta_value * np.mean(benchmark_excess_returns)

def sortino_ratio(returns, risk_free_rate=0):
    """
    Calculate the Sortino ratio.

    :param returns: Array or list of return values.
    :param risk_free_rate: The risk-free rate for Sortino ratio calculation.
    :return: Sortino ratio value.
    """
    downside_returns = returns[returns < risk_free_rate]
    return np.mean(returns - risk_free_rate) / np.std(downside_returns)

def rolling_volatility(data, window_size):
    """
    Calculate the rolling volatility over a specified window size.

    :param data: Array or list of price data.
    :param window_size: Size of the rolling window.
    :return: Array of rolling volatility values.
    """
    return np.array([np.std(data[i:i + window_size]) for i in range(len(data) - window_size + 1)])
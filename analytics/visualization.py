import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load market data from a CSV file
def load_market_data(filepath):
    return pd.read_csv(filepath)

# Function to plot historical price data using matplotlib
def plot_price_data(price_data, title="Price Data", xlabel="Timestamp", ylabel="Price"):
    plt.figure(figsize=(12, 7))
    plt.plot(price_data['timestamp'], price_data['price'], label='Price', color='blue', linewidth=1.5)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to plot volume data using Plotly
def plot_volume_data(volume_data, title="Volume Data"):
    fig = go.Figure(data=[
        go.Bar(x=volume_data['timestamp'], y=volume_data['volume'], name='Volume', marker_color='orange')
    ])
    fig.update_layout(title=title, xaxis_title='Timestamp', yaxis_title='Volume', bargap=0.2)
    fig.show()

# Function to visualize Profit and Loss (PnL) data using matplotlib
def plot_pnl_data(pnl_data, title="PnL Data", xlabel="Timestamp", ylabel="PnL"):
    plt.figure(figsize=(12, 7))
    plt.plot(pnl_data['timestamp'], pnl_data['pnl'], label='PnL', color='green', linewidth=1.5)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to visualize drawdown using matplotlib
def plot_drawdown(drawdown_data, title="Drawdown", xlabel="Timestamp", ylabel="Drawdown"):
    plt.figure(figsize=(12, 7))
    plt.plot(drawdown_data['timestamp'], drawdown_data['drawdown'], label='Drawdown', color='red', linewidth=1.5)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to visualize Sharpe Ratio and Max Drawdown using Plotly
def plot_risk_metrics(risk_metrics, title="Risk Metrics", xlabel="Timestamp"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=risk_metrics['timestamp'], y=risk_metrics['sharpe_ratio'], mode='lines', name='Sharpe Ratio', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=risk_metrics['timestamp'], y=risk_metrics['max_drawdown'], mode='lines', name='Max Drawdown', line=dict(color='red')))
    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title='Metric Value', hovermode='x unified')
    fig.show()

# Function to visualize the order book data with bids and asks
def plot_order_book(order_book_data, title="Order Book Depth", xlabel="Price", ylabel="Volume"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=order_book_data['price'], y=order_book_data['bids'], mode='lines', name='Bids', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=order_book_data['price'], y=order_book_data['asks'], mode='lines', name='Asks', line=dict(color='red')))
    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel)
    fig.show()

# Function to plot a heatmap of price correlation
def plot_correlation_heatmap(price_data, title="Price Correlation Heatmap"):
    plt.figure(figsize=(10, 8))
    corr_matrix = price_data.corr()
    cax = plt.matshow(corr_matrix, cmap='coolwarm', fignum=1)
    plt.colorbar(cax)
    ticks = np.arange(0, len(corr_matrix.columns), 1)
    plt.xticks(ticks, corr_matrix.columns, rotation=90)
    plt.yticks(ticks, corr_matrix.columns)
    plt.title(title, fontsize=16)
    plt.show()

# Function to plot moving averages (SMA, EMA) for trend analysis
def plot_moving_averages(price_data, window_sma=20, window_ema=20, title="Moving Averages", xlabel="Timestamp", ylabel="Price"):
    price_data['SMA'] = price_data['price'].rolling(window=window_sma).mean()
    price_data['EMA'] = price_data['price'].ewm(span=window_ema, adjust=False).mean()

    plt.figure(figsize=(12, 7))
    plt.plot(price_data['timestamp'], price_data['price'], label='Price', color='blue', linewidth=1.5)
    plt.plot(price_data['timestamp'], price_data['SMA'], label=f'SMA {window_sma}', color='orange', linestyle='--', linewidth=1.5)
    plt.plot(price_data['timestamp'], price_data['EMA'], label=f'EMA {window_ema}', color='green', linestyle='--', linewidth=1.5)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to calculate and plot volatility (using rolling standard deviation)
def plot_volatility(price_data, window=20, title="Volatility (Rolling Std Dev)", xlabel="Timestamp", ylabel="Volatility"):
    price_data['Volatility'] = price_data['price'].rolling(window=window).std()

    plt.figure(figsize=(12, 7))
    plt.plot(price_data['timestamp'], price_data['Volatility'], label=f'Volatility {window}-period', color='purple', linewidth=1.5)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to visualize cumulative returns
def plot_cumulative_returns(price_data, title="Cumulative Returns", xlabel="Timestamp", ylabel="Cumulative Return"):
    price_data['Cumulative Return'] = (1 + price_data['price'].pct_change()).cumprod() - 1

    plt.figure(figsize=(12, 7))
    plt.plot(price_data['timestamp'], price_data['Cumulative Return'], label='Cumulative Return', color='brown', linewidth=1.5)
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Usage
if __name__ == "__main__":
    # File paths
    price_data = load_market_data('data/price_data.csv')
    volume_data = load_market_data('data/volume_data.csv')
    pnl_data = load_market_data('data/pnl_data.csv')
    drawdown_data = load_market_data('data/drawdown_data.csv')
    risk_metrics = load_market_data('data/risk_metrics.csv')
    order_book_data = load_market_data('data/order_book_data.csv')

    # Visualization calls
    plot_price_data(price_data)
    plot_volume_data(volume_data)
    plot_pnl_data(pnl_data)
    plot_drawdown(drawdown_data)
    plot_risk_metrics(risk_metrics)
    plot_order_book(order_book_data)

    # Additional visualizations
    plot_moving_averages(price_data)
    plot_volatility(price_data)
    plot_cumulative_returns(price_data)
    plot_correlation_heatmap(price_data)
import os
import pandas as pd
import matplotlib.pyplot as plt
from analytics.performance_metrics import calculate_sharpe_ratio, calculate_drawdown, calculate_slippage
from utils.time_utils import format_timestamp

# Directory containing trading session data
data_dir = "data/processed/"

# File to save the generated report
report_file = "reports/performance_report.txt"

def load_trading_data(file_path):
    """Load processed trading data from the specified file."""
    return pd.read_csv(file_path)

def generate_performance_report(trading_data):
    """Generate a detailed performance report based on the trading data."""
    
    # Calculate key performance metrics
    sharpe_ratio = calculate_sharpe_ratio(trading_data['returns'])
    max_drawdown = calculate_drawdown(trading_data['equity_curve'])
    slippage = calculate_slippage(trading_data['slippage'])
    
    # Prepare the report
    report_content = f"""
    Performance Report:
    ====================
    
    Sharpe Ratio: {sharpe_ratio:.2f}
    Max Drawdown: {max_drawdown:.2f}%
    Total Slippage: {slippage:.4f}
    
    Summary of Trades:
    ------------------
    Total Trades: {len(trading_data)}
    Winning Trades: {len(trading_data[trading_data['pnl'] > 0])}
    Losing Trades: {len(trading_data[trading_data['pnl'] <= 0])}
    
    Profit/Loss Overview:
    ---------------------
    Total Profit/Loss: {trading_data['pnl'].sum():.2f}
    Average Profit per Trade: {trading_data['pnl'].mean():.2f}
    """
    
    return report_content

def plot_performance(trading_data):
    """Generate and save performance visualizations."""
    
    # Plot the equity curve
    plt.figure(figsize=(10, 6))
    plt.plot(trading_data['timestamp'], trading_data['equity_curve'], label='Equity Curve')
    plt.xlabel('Time')
    plt.ylabel('Equity')
    plt.title('Equity Curve Over Time')
    plt.legend()
    plt.savefig('reports/equity_curve.png')
    
    # Plot the returns over time
    plt.figure(figsize=(10, 6))
    plt.plot(trading_data['timestamp'], trading_data['returns'], label='Returns', color='green')
    plt.xlabel('Time')
    plt.ylabel('Returns')
    plt.title('Returns Over Time')
    plt.legend()
    plt.savefig('reports/returns_over_time.png')

def save_report(report_content):
    """Save the generated report to a file."""
    with open(report_file, 'w') as f:
        f.write(report_content)

def main():
    # Load the most recent trading data
    latest_data_file = sorted([os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')])[-1]
    trading_data = load_trading_data(latest_data_file)
    
    # Format timestamps
    trading_data['timestamp'] = trading_data['timestamp'].apply(format_timestamp)
    
    # Generate the performance report
    report_content = generate_performance_report(trading_data)
    
    # Save the performance report
    save_report(report_content)
    
    # Generate performance visualizations
    plot_performance(trading_data)
    
    print(f"Performance report and visualizations have been saved to the 'reports/' directory.")

if __name__ == "__main__":
    main()
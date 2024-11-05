# Trading Strategies

## Overview

The HFT system supports various types of trading strategies designed for different market conditions and goals. Each strategy is modular and can be optimized based on specific parameters.

### Strategy Types

1. **Momentum Strategy (C++)**:
   - Focuses on short-term price movements.
   - Identifies upward or downward trends and places trades accordingly.
   - File: `strategies/momentum/momentum_strategy.cpp`.

2. **Mean Reversion Strategy (Python)**:
   - Exploits deviations from the mean price.
   - Places trades expecting the price to revert to its historical average.
   - File: `strategies/mean_reversion/mean_reversion_strategy.py`.

3. **Statistical Arbitrage (Java)**:
   - Capitalizes on price discrepancies between different instruments or markets.
   - Involves sophisticated statistical models for price forecasting.
   - File: `strategies/arbitrage/statistical_arbitrage.java`.

4. **Market-Making Strategy (Java)**:
   - Provides liquidity by continuously placing buy and sell limit orders.
   - Captures the bid-ask spread as profit.
   - File: `strategies/market_making/market_making_strategy.java`.

### Backtesting and Simulation

- **Backtesting**: The system includes a backtesting tool to simulate historical data and optimize strategy parameters.
  - File: `strategies/backtest.py`.
  
- **Simulation**: Simulates strategies in controlled environments to assess behavior under various market conditions.
  - File: `strategies/simulate.py`.
  
- **Optimization**: Fine-tunes strategy parameters using historical data.
  - File: `strategies/optimize.py`.

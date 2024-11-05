#include <iostream>
#include <vector>
#include <numeric>  
#include <algorithm> 
#include <cmath> 
#include <ctime>   
#include <iomanip>  
#include <fstream> 

// Utility function to print a line separator for better output readability
void printSeparator() {
    std::cout << "------------------------------------" << std::endl;
}

// Class to manage the moving average calculations for momentum
class MovingAverage {
private:
    int period;
    std::vector<double> values;

public:
    MovingAverage(int p) : period(p) {}

    void addValue(double value) {
        values.push_back(value);
        if (values.size() > period) {
            values.erase(values.begin());
        }
    }

    double getAverage() const {
        if (values.size() < period) {
            return 0.0; // Not enough data to compute average
        }
        double sum = std::accumulate(values.begin(), values.end(), 0.0);
        return sum / values.size();
    }

    int getPeriod() const {
        return period;
    }

    bool isReady() const {
        return values.size() >= period;
    }
};

// Main Momentum Strategy Class
class MomentumStrategy {
private:
    std::vector<double> prices;
    int lookback_period;
    double momentum_threshold;
    double position_size;
    bool position_open;
    MovingAverage short_term_ma;
    MovingAverage long_term_ma;

public:
    // Constructor to initialize the strategy parameters
    MomentumStrategy(int short_ma_period, int long_ma_period, double threshold, double size)
        : lookback_period(short_ma_period), momentum_threshold(threshold), position_size(size),
          position_open(false), short_term_ma(short_ma_period), long_term_ma(long_ma_period) {}

    // Function to calculate the momentum
    double calculateMomentum() {
        if (prices.size() < lookback_period) {
            return 0.0; // Not enough data
        }
        double momentum = (prices.back() - prices[prices.size() - lookback_period]) / prices[prices.size() - lookback_period];
        return momentum;
    }

    // Function to calculate the short-term and long-term moving averages
    void calculateMovingAverages(double price) {
        short_term_ma.addValue(price);
        long_term_ma.addValue(price);
    }

    // Function to process new price data and check for trading signals
    void onNewPrice(double price) {
        prices.push_back(price);
        calculateMovingAverages(price);

        if (prices.size() > lookback_period) {
            double momentum = calculateMomentum();
            if (momentum > momentum_threshold && !position_open && short_term_ma.isReady() && long_term_ma.isReady()) {
                if (short_term_ma.getAverage() > long_term_ma.getAverage()) {
                    buy();
                }
            } else if (momentum < -momentum_threshold && position_open) {
                sell();
            }
        }
    }

    // Execute buy order
    void buy() {
        std::cout << "Momentum detected: BUY at price " << prices.back() << std::endl;
        printSeparator();
        position_open = true;
    }

    // Execute sell order
    void sell() {
        std::cout << "Momentum detected: SELL at price " << prices.back() << std::endl;
        printSeparator();
        position_open = false;
    }

    // Reset the strategy, useful when switching between instruments
    void reset() {
        prices.clear();
        position_open = false;
    }

    // Print the price history (for monitoring purposes)
    void printPrices() const {
        std::cout << "Price history: ";
        for (const auto& p : prices) {
            std::cout << p << " ";
        }
        std::cout << std::endl;
        printSeparator();
    }

    // Display moving averages for debugging purposes
    void displayMovingAverages() const {
        std::cout << "Short-term MA: " << short_term_ma.getAverage() << std::endl;
        std::cout << "Long-term MA: " << long_term_ma.getAverage() << std::endl;
        printSeparator();
    }
};

// Utility class to handle statistical calculations like volatility
class Statistics {
public:
    static double calculateVolatility(const std::vector<double>& prices) {
        if (prices.size() < 2) {
            return 0.0;
        }
        double mean = std::accumulate(prices.begin(), prices.end(), 0.0) / prices.size();
        double variance = 0.0;

        for (double price : prices) {
            variance += std::pow(price - mean, 2);
        }
        variance /= prices.size();
        return std::sqrt(variance);
    }
};

int main() {
    // Initialize the strategy with a short-term MA of 5, long-term MA of 10, and a momentum threshold of 0.02
    MomentumStrategy strategy(5, 10, 0.02, 1000);

    // Price data feed
    std::vector<double> price_feed = {100.5, 101.0, 101.8, 102.5, 103.0, 104.0, 105.2, 106.0, 107.5, 108.2, 109.0};

    // Feed prices into the strategy
    for (double price : price_feed) {
        strategy.onNewPrice(price);
        strategy.printPrices(); // Print price history after every new price
        strategy.displayMovingAverages(); // Display moving averages for monitoring
    }

    // Calculate volatility of the price series
    double volatility = Statistics::calculateVolatility(price_feed);
    std::cout << "Calculated volatility: " << volatility << std::endl;
    printSeparator();

    return 0;
}

// Class to handle risk management
class RiskManager {
private:
    double max_position_size;
    double max_drawdown;
    double current_position_size;
    double peak_equity;
    double current_equity;

public:
    RiskManager(double max_pos_size, double max_dd) 
        : max_position_size(max_pos_size), max_drawdown(max_dd), current_position_size(0.0), peak_equity(0.0), current_equity(0.0) {}

    // Update the current equity and adjust peak equity
    void updateEquity(double new_equity) {
        current_equity = new_equity;
        if (current_equity > peak_equity) {
            peak_equity = current_equity;
        }
    }

    // Check if current position size exceeds risk limits
    bool checkPositionSize(double size) {
        current_position_size = size;
        return current_position_size <= max_position_size;
    }

    // Check if drawdown exceeds the allowed maximum
    bool checkDrawdown() {
        double drawdown = (peak_equity - current_equity) / peak_equity;
        return drawdown <= max_drawdown;
    }

    // Print current risk stats
    void printRiskStatus() const {
        std::cout << "Current Equity: " << current_equity << ", Peak Equity: " << peak_equity << std::endl;
        std::cout << "Max Drawdown Allowed: " << max_drawdown * 100 << "%, Current Drawdown: " 
                  << ((peak_equity - current_equity) / peak_equity) * 100 << "%" << std::endl;
        printSeparator();
    }
};

// Class to log strategy performance
class Logger {
private:
    std::ofstream log_file;
    
public:
    Logger(const std::string& filename) {
        log_file.open(filename, std::ios::app);
        if (!log_file.is_open()) {
            std::cerr << "Failed to open log file!" << std::endl;
        }
    }

    ~Logger() {
        if (log_file.is_open()) {
            log_file.close();
        }
    }

    // Log strategy actions with timestamps
    void logAction(const std::string& action, double price) {
        if (log_file.is_open()) {
            auto now = std::time(0);
            std::tm* ltm = std::localtime(&now);
            log_file << "[" << 1900 + ltm->tm_year << "-"
                     << 1 + ltm->tm_mon << "-"
                     << ltm->tm_mday << " "
                     << std::setw(2) << std::setfill('0') << ltm->tm_hour << ":"
                     << std::setw(2) << std::setfill('0') << ltm->tm_min << ":"
                     << std::setw(2) << std::setfill('0') << ltm->tm_sec << "] "
                     << action << " at price " << price << std::endl;
        }
    }
};

// Enhanced Momentum Strategy with Risk and Logging
class EnhancedMomentumStrategy {
private:
    std::vector<double> prices;
    int lookback_period;
    double momentum_threshold;
    double position_size;
    bool position_open;
    MovingAverage short_term_ma;
    MovingAverage long_term_ma;
    RiskManager risk_manager;
    Logger logger;
    double equity;

public:
    // Constructor initializing all parameters, risk manager, and logger
    EnhancedMomentumStrategy(int short_ma_period, int long_ma_period, double threshold, double size, double max_pos, double max_dd, const std::string& log_filename)
        : lookback_period(short_ma_period), momentum_threshold(threshold), position_size(size), position_open(false),
          short_term_ma(short_ma_period), long_term_ma(long_ma_period),
          risk_manager(max_pos, max_dd), logger(log_filename), equity(100000) // Start with an initial equity of 100k
    {}

    // Calculate momentum
    double calculateMomentum() {
        if (prices.size() < lookback_period) {
            return 0.0; // Not enough data
        }
        return (prices.back() - prices[prices.size() - lookback_period]) / prices[prices.size() - lookback_period];
    }

    // Calculate moving averages
    void calculateMovingAverages(double price) {
        short_term_ma.addValue(price);
        long_term_ma.addValue(price);
    }

    // Process new price data and check for trading signals
    void onNewPrice(double price) {
        prices.push_back(price);
        calculateMovingAverages(price);

        // Update equity after each price, consider it simple mark-to-market for the sake of logging and risk management
        updateEquity(price);

        if (prices.size() > lookback_period) {
            double momentum = calculateMomentum();
            if (momentum > momentum_threshold && !position_open && short_term_ma.isReady() && long_term_ma.isReady()) {
                if (short_term_ma.getAverage() > long_term_ma.getAverage() && risk_manager.checkPositionSize(position_size)) {
                    buy(price);
                }
            } else if (momentum < -momentum_threshold && position_open) {
                sell(price);
            }
        }
        risk_manager.printRiskStatus();
    }

    // Execute buy order
    void buy(double price) {
        std::cout << "Momentum detected: BUY at price " << price << std::endl;
        printSeparator();
        position_open = true;
        logger.logAction("BUY", price);
        equity -= position_size * price; // Update equity to account for the position
    }

    // Execute sell order
    void sell(double price) {
        std::cout << "Momentum detected: SELL at price " << price << std::endl;
        printSeparator();
        position_open = false;
        logger.logAction("SELL", price);
        equity += position_size * price; // Update equity to account for closing position
    }

    // Update equity
    void updateEquity(double price) {
        if (position_open) {
            double current_value = position_size * price;
            risk_manager.updateEquity(equity + current_value); // Mark-to-market equity update
        } else {
            risk_manager.updateEquity(equity); // Flat position, no change in equity
        }
    }

    // Reset the strategy for a new session
    void reset() {
        prices.clear();
        position_open = false;
        equity = 100000; // Reset equity to initial value
    }

    // Display prices and moving averages (for monitoring)
    void printPrices() const {
        std::cout << "Price history: ";
        for (const auto& p : prices) {
            std::cout << p << " ";
        }
        std::cout << std::endl;
        printSeparator();
    }

    // Display moving averages for monitoring purposes
    void displayMovingAverages() const {
        std::cout << "Short-term MA: " << short_term_ma.getAverage() << std::endl;
        std::cout << "Long-term MA: " << long_term_ma.getAverage() << std::endl;
        printSeparator();
    }
};

int main() {
    // Initialize the enhanced strategy with logging and risk management
    EnhancedMomentumStrategy strategy(5, 10, 0.02, 1000, 5000, 0.2, "strategy_log.txt");

    // Simulated price data feed
    std::vector<double> price_feed = {100.5, 101.0, 101.8, 102.5, 103.0, 104.0, 105.2, 106.0, 107.5, 108.2, 109.0};

    // Feed prices into the strategy
    for (double price : price_feed) {
        strategy.onNewPrice(price);
        strategy.printPrices(); // Print price history after every new price
        strategy.displayMovingAverages(); // Display moving averages for monitoring
    }

    return 0;
}
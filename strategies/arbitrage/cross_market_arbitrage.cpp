#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <thread>
#include "exchange_connector.h" 
#include "order_manager.h"      
#include "log_utils.h"         

// Constants
const double PRICE_DIFF_THRESHOLD = 0.05;  
const int MAX_POSITION_SIZE = 100;         
const int SLEEP_DURATION_MS = 100;         

// Structure to hold market data from an exchange
struct MarketData {
    double price;
    double volume;
    std::chrono::time_point<std::chrono::system_clock> timestamp;

    MarketData(double p, double v) : price(p), volume(v) {
        timestamp = std::chrono::system_clock::now();
    }
};

// Function to fetch market data from multiple exchanges
MarketData getMarketData(ExchangeConnector& exchange) {
    double price = exchange.getLatestPrice();
    double volume = exchange.getLatestVolume();
    return MarketData(price, volume);
}

// Function to log the current market data for debugging purposes
void logMarketData(const MarketData& data, const std::string& exchangeName) {
    std::time_t timestamp = std::chrono::system_clock::to_time_t(data.timestamp);
    log_info("Market Data from " + exchangeName + ": Price = " + std::to_string(data.price) + 
             ", Volume = " + std::to_string(data.volume) + 
             ", Timestamp = " + std::ctime(&timestamp));
}

// Function to check arbitrage opportunity based on price difference between two markets
bool checkArbitrageOpportunity(const MarketData& data1, const MarketData& data2) {
    double priceDifference = std::abs(data1.price - data2.price);
    log_info("Price Difference: " + std::to_string(priceDifference));

    return priceDifference >= PRICE_DIFF_THRESHOLD;
}

// Function to execute arbitrage trade between two exchanges
void executeArbitrageTrade(ExchangeConnector& exchange1, ExchangeConnector& exchange2, double amount) {
    log_info("Arbitrage opportunity detected, executing trades.");

    // Determine which exchange has the lower price and place respective buy/sell orders
    if (exchange1.getLatestPrice() < exchange2.getLatestPrice()) {
        log_info("Buying on Exchange 1, Selling on Exchange 2.");
        exchange1.placeOrder(OrderType::BUY, amount);
        exchange2.placeOrder(OrderType::SELL, amount);
    } else {
        log_info("Buying on Exchange 2, Selling on Exchange 1.");
        exchange2.placeOrder(OrderType::BUY, amount);
        exchange1.placeOrder(OrderType::SELL, amount);
    }

    log_info("Arbitrage trade executed successfully.");
}

// Function to update order status in order manager after each trade
void updateOrderStatus(OrderManager& orderManager) {
    log_info("Updating order statuses.");
    orderManager.updateOrderStatus();
}

// Main function to execute cross-market arbitrage strategy
void crossMarketArbitrage(ExchangeConnector& exchange1, ExchangeConnector& exchange2, OrderManager& orderManager) {
    while (true) {
        // Fetch latest market data from both exchanges
        log_info("Fetching market data from Exchange 1 and Exchange 2.");
        MarketData marketData1 = getMarketData(exchange1);
        MarketData marketData2 = getMarketData(exchange2);

        // Log the market data for monitoring
        logMarketData(marketData1, "Exchange 1");
        logMarketData(marketData2, "Exchange 2");

        // Check if an arbitrage opportunity exists between the two exchanges
        if (checkArbitrageOpportunity(marketData1, marketData2)) {
            // Calculate the amount to trade, based on available volumes and position limits
            double arbitrageAmount = std::min(marketData1.volume, marketData2.volume);
            arbitrageAmount = std::min(arbitrageAmount, static_cast<double>(MAX_POSITION_SIZE));

            log_info("Arbitrage Amount: " + std::to_string(arbitrageAmount));

            // Execute the arbitrage trade
            executeArbitrageTrade(exchange1, exchange2, arbitrageAmount);

            // Update order status in the order manager
            updateOrderStatus(orderManager);
        }

        // Sleep to avoid excessive API requests to the exchanges
        log_info("Sleeping for " + std::to_string(SLEEP_DURATION_MS) + " milliseconds.");
        std::this_thread::sleep_for(std::chrono::milliseconds(SLEEP_DURATION_MS));
    }
}

// Main entry point of the program
int main() {
    // Initialize exchange connectors for two different markets
    log_info("Initializing exchange connectors for Exchange 1 and Exchange 2.");
    ExchangeConnector exchange1("https://exchange1.com");
    ExchangeConnector exchange2("https://exchange2.com");

    // Initialize the order manager
    log_info("Initializing order manager.");
    OrderManager orderManager;

    // Start the cross-market arbitrage strategy
    log_info("Starting cross-market arbitrage strategy.");
    crossMarketArbitrage(exchange1, exchange2, orderManager);

    return 0;
}

// Additional functionality to monitor performance and metrics
struct PerformanceMetrics {
    double totalProfit;
    int totalTrades;
    int successfulArbitrages;
    int failedArbitrages;

    PerformanceMetrics() : totalProfit(0), totalTrades(0), successfulArbitrages(0), failedArbitrages(0) {}

    void logMetrics() const {
        log_info("Performance Metrics:");
        log_info("Total Profit: " + std::to_string(totalProfit));
        log_info("Total Trades: " + std::to_string(totalTrades));
        log_info("Successful Arbitrages: " + std::to_string(successfulArbitrages));
        log_info("Failed Arbitrages: " + std::to_string(failedArbitrages));
    }

    void updateMetrics(double profit, bool success) {
        totalProfit += profit;
        totalTrades++;
        if (success) {
            successfulArbitrages++;
        } else {
            failedArbitrages++;
        }
    }
};

// Function to calculate the profit from an arbitrage trade
double calculateProfit(const MarketData& data1, const MarketData& data2, double amount) {
    double buyPrice, sellPrice;
    if (data1.price < data2.price) {
        buyPrice = data1.price;
        sellPrice = data2.price;
    } else {
        buyPrice = data2.price;
        sellPrice = data1.price;
    }

    double profit = (sellPrice - buyPrice) * amount;
    log_info("Profit from arbitrage trade: " + std::to_string(profit));
    return profit;
}

// Enhanced execution of arbitrage trade with performance tracking
void executeArbitrageTradeWithMetrics(ExchangeConnector& exchange1, ExchangeConnector& exchange2, 
                                      double amount, PerformanceMetrics& metrics) {
    try {
        // Execute the arbitrage trade and calculate profit
        double profit = calculateProfit(getMarketData(exchange1), getMarketData(exchange2), amount);

        // Execute the buy and sell operations
        if (exchange1.getLatestPrice() < exchange2.getLatestPrice()) {
            exchange1.placeOrder(OrderType::BUY, amount);
            exchange2.placeOrder(OrderType::SELL, amount);
        } else {
            exchange2.placeOrder(OrderType::BUY, amount);
            exchange1.placeOrder(OrderType::SELL, amount);
        }

        // Update performance metrics
        metrics.updateMetrics(profit, true);
        log_info("Arbitrage trade executed and metrics updated.");
    } catch (const std::exception& e) {
        log_error("Error during arbitrage execution: " + std::string(e.what()));
        metrics.updateMetrics(0, false);
    }
}

// Function to display detailed performance statistics periodically
void displayPerformanceStatistics(PerformanceMetrics& metrics) {
    while (true) {
        // Log and display metrics every minute
        metrics.logMetrics();
        std::this_thread::sleep_for(std::chrono::minutes(1));
    }
}

// Main function to execute cross-market arbitrage with performance tracking
void crossMarketArbitrageWithMetrics(ExchangeConnector& exchange1, ExchangeConnector& exchange2, 
                                     OrderManager& orderManager, PerformanceMetrics& metrics) {
    // Launch a separate thread to display performance statistics periodically
    std::thread performanceThread(displayPerformanceStatistics, std::ref(metrics));
    performanceThread.detach();

    while (true) {
        // Fetch latest market data from both exchanges
        MarketData marketData1 = getMarketData(exchange1);
        MarketData marketData2 = getMarketData(exchange2);

        // Log the market data for monitoring
        logMarketData(marketData1, "Exchange 1");
        logMarketData(marketData2, "Exchange 2");

        // Check if an arbitrage opportunity exists between the two exchanges
        if (checkArbitrageOpportunity(marketData1, marketData2)) {
            double arbitrageAmount = std::min(marketData1.volume, marketData2.volume);
            arbitrageAmount = std::min(arbitrageAmount, static_cast<double>(MAX_POSITION_SIZE));

            // Execute the arbitrage trade with performance tracking
            executeArbitrageTradeWithMetrics(exchange1, exchange2, arbitrageAmount, metrics);

            // Update order status in the order manager
            updateOrderStatus(orderManager);
        }

        // Sleep between iterations to avoid overwhelming the exchanges
        std::this_thread::sleep_for(std::chrono::milliseconds(SLEEP_DURATION_MS));
    }
}

int main() {
    // Initialize exchange connectors for two different markets
    log_info("Initializing exchange connectors for Exchange 1 and Exchange 2.");
    ExchangeConnector exchange1("https://exchange1.com");
    ExchangeConnector exchange2("https://exchange2.com");

    // Initialize the order manager
    log_info("Initializing order manager.");
    OrderManager orderManager;

    // Initialize performance metrics tracker
    log_info("Initializing performance metrics.");
    PerformanceMetrics metrics;

    // Start the cross-market arbitrage strategy with performance tracking
    log_info("Starting cross-market arbitrage strategy with performance tracking.");
    crossMarketArbitrageWithMetrics(exchange1, exchange2, orderManager, metrics);

    return 0;
}
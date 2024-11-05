#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <thread>
#include <mutex>
#include <atomic>
#include <fstream>
#include <pybind11/embed.h> 
#include <jni.h> 

std::atomic<bool> running(true);
std::mutex data_mutex;

// Structure to hold live market and strategy data
struct DashboardData {
    std::vector<double> market_prices;
    std::vector<double> performance_metrics;
    double risk_exposure;
    double latency;
    double volatility;
    double spread;
};

// Function to log data to file
void logData(const DashboardData& data) {
    std::ofstream log_file("dashboard_log.txt", std::ios_base::app);
    if (log_file.is_open()) {
        log_file << "------ Log Entry ------\n";
        log_file << "Market Prices: ";
        for (const auto& price : data.market_prices) {
            log_file << price << " ";
        }
        log_file << "\nPerformance Metrics: ";
        for (const auto& metric : data.performance_metrics) {
            log_file << metric << " ";
        }
        log_file << "\nRisk Exposure: " << data.risk_exposure << "\n";
        log_file << "Latency: " << data.latency << " ms\n";
        log_file << "Volatility: " << data.volatility << "\n";
        log_file << "Spread: " << data.spread << "\n";
        log_file << "-----------------------\n";
    }
    log_file.close();
}

// Function to fetch live market data
void fetchMarketData(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        data.market_prices = getLiveMarketData();
        data.volatility = getMarketVolatility();  // Fetching volatility metric
        data.spread = getMarketSpread();          // Fetching bid-ask spread
        logData(data);  // Log the fetched data
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Simulate real-time feed delay
    }
}

// Function to fetch live strategy performance data
void fetchPerformanceData(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        data.performance_metrics = getStrategyPerformance();
        logData(data);  // Log the performance data
        std::this_thread::sleep_for(std::chrono::milliseconds(200)); // Simulate data update interval
    }
}

// Function to fetch live risk exposure data
void fetchRiskData(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        data.risk_exposure = getRiskExposure();
        logData(data);  // Log the risk data
        std::this_thread::sleep_for(std::chrono::milliseconds(300)); // Simulate real-time risk management update
    }
}

// Function to monitor execution latency
void monitorLatency(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        data.latency = getExecutionLatency();
        logData(data);  // Log the latency data
        std::this_thread::sleep_for(std::chrono::milliseconds(150)); // Simulate latency monitoring interval
    }
}

// Function to generate random warnings based on risk exposure and volatility
void generateWarnings(const DashboardData& data) {
    if (data.risk_exposure > 1000000) {
        std::cerr << "WARNING: Risk exposure exceeded safe limits!" << std::endl;
    }
    if (data.volatility > 2.5) {
        std::cerr << "WARNING: Market volatility is very high!" << std::endl;
    }
    if (data.latency > 500) {
        std::cerr << "WARNING: Execution latency is too high!" << std::endl;
    }
}

// Function to display real-time data on the dashboard
void displayDashboard(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        std::cout << "------ Live Monitoring Dashboard ------\n";
        std::cout << "Market Prices: ";
        for (const auto& price : data.market_prices) {
            std::cout << price << " ";
        }
        std::cout << "\nPerformance Metrics: ";
        for (const auto& metric : data.performance_metrics) {
            std::cout << metric << " ";
        }
        std::cout << "\nRisk Exposure: " << data.risk_exposure << "\n";
        std::cout << "Latency: " << data.latency << " ms\n";
        std::cout << "Volatility: " << data.volatility << "\n";
        std::cout << "Spread: " << data.spread << "\n";
        std::cout << "---------------------------------------\n";
        
        generateWarnings(data);  // Check for warnings
        std::this_thread::sleep_for(std::chrono::seconds(1)); // Update dashboard every second
    }
}

// Extended data fetching for deeper market conditions
void fetchAdditionalMetrics(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        data.volatility = getMarketVolatility();   // Simulate fetching market volatility
        data.spread = getMarketSpread();           // Simulate fetching market bid-ask spread
        std::this_thread::sleep_for(std::chrono::milliseconds(500)); // Update additional metrics periodically
    }
}

// Function to display extended data on the dashboard
void displayExtendedMetrics(const DashboardData& data) {
    std::cout << "Additional Metrics:\n";
    std::cout << "Market Volatility: " << data.volatility << "\n";
    std::cout << "Bid-Ask Spread: " << data.spread << "\n";
}

// Extended real-time data display with logging and additional metrics
void displayCompleteDashboard(DashboardData& data) {
    while (running) {
        std::lock_guard<std::mutex> lock(data_mutex);
        std::cout << "****** Complete Live Monitoring Dashboard ******\n";
        std::cout << "Market Prices: ";
        for (const auto& price : data.market_prices) {
            std::cout << price << " ";
        }
        std::cout << "\nPerformance Metrics: ";
        for (const auto& metric : data.performance_metrics) {
            std::cout << metric << " ";
        }
        std::cout << "\nRisk Exposure: " << data.risk_exposure << "\n";
        std::cout << "Latency: " << data.latency << " ms\n";
        std::cout << "Volatility: " << data.volatility << "\n";
        std::cout << "Spread: " << data.spread << "\n";
        std::cout << "***********************************************\n";
        
        generateWarnings(data);  // Generate warning messages
        logData(data);  // Log the data to file for historical tracking
        displayExtendedMetrics(data);  // Display extended metrics
        
        std::this_thread::sleep_for(std::chrono::seconds(1)); // Update dashboard every second
    }
}

int main() {
    DashboardData dashboard_data;

    // Launch threads for live data monitoring
    std::thread market_data_thread(fetchMarketData, std::ref(dashboard_data));
    std::thread performance_data_thread(fetchPerformanceData, std::ref(dashboard_data));
    std::thread risk_data_thread(fetchRiskData, std::ref(dashboard_data));
    std::thread latency_monitor_thread(monitorLatency, std::ref(dashboard_data));
    std::thread additional_metrics_thread(fetchAdditionalMetrics, std::ref(dashboard_data));
    std::thread display_thread(displayCompleteDashboard, std::ref(dashboard_data));

    // Run the dashboard for a defined duration (60 seconds)
    std::this_thread::sleep_for(std::chrono::seconds(60));
    running = false;

    // Wait for all threads to finish
    market_data_thread.join();
    performance_data_thread.join();
    risk_data_thread.join();
    latency_monitor_thread.join();
    additional_metrics_thread.join();
    display_thread.join();

    return 0;
}
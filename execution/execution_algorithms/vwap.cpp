#include <iostream>
#include <vector>
#include <numeric>
#include <fstream>
#include <ctime>
#include <iomanip>
#include <cmath>

// Helper function to get current timestamp
std::string getCurrentTimestamp() {
    std::time_t now = std::time(nullptr);
    std::tm *ltm = std::localtime(&now);
    char buffer[20];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", ltm);
    return std::string(buffer);
}

// Class to log VWAP executions
class VWAPLogger {
private:
    std::ofstream logFile;

public:
    VWAPLogger(const std::string &filename) {
        logFile.open(filename, std::ios::out | std::ios::app);
        if (!logFile.is_open()) {
            std::cerr << "Error: Unable to open log file." << std::endl;
        }
    }

    ~VWAPLogger() {
        if (logFile.is_open()) {
            logFile.close();
        }
    }

    void logExecution(const std::string &timestamp, double vwap, double target, bool executed) {
        if (logFile.is_open()) {
            logFile << timestamp << " | VWAP: " << std::fixed << std::setprecision(2)
                    << vwap << " | Target: " << target
                    << " | Executed: " << (executed ? "Yes" : "No") << std::endl;
        }
    }
};

// VWAP Execution Class
class VWAPExecution {
private:
    std::vector<double> prices;
    std::vector<double> volumes;
    std::vector<double> executionPrices;
    std::vector<double> executionVolumes;
    double totalVolume;
    double totalPriceVolume;
    VWAPLogger logger;
    int totalExecutions;
    int totalNonExecutions;
    double totalExecutedVolume;

public:
    VWAPExecution(const std::string &logFilename)
        : totalVolume(0), totalPriceVolume(0), logger(logFilename), totalExecutions(0), totalNonExecutions(0), totalExecutedVolume(0) {}

    // Add market data (price and volume) to the computation
    void addMarketData(double price, double volume) {
        prices.push_back(price);
        volumes.push_back(volume);

        totalPriceVolume += price * volume;
        totalVolume += volume;
    }

    // Compute the current VWAP based on collected data
    double calculateVWAP() const {
        if (totalVolume == 0) return 0;
        return totalPriceVolume / totalVolume;
    }

    // Execute an order based on the VWAP price and target price
    void executeOrder(double targetVWAP) {
        double currentVWAP = calculateVWAP();
        std::string timestamp = getCurrentTimestamp();
        bool executed = false;

        if (currentVWAP <= targetVWAP) {
            double executionVolume = getExecutionVolume(currentVWAP, targetVWAP);
            executionPrices.push_back(currentVWAP);
            executionVolumes.push_back(executionVolume);
            totalExecutions++;
            totalExecutedVolume += executionVolume;
            executed = true;
            std::cout << timestamp << " | Executing order at VWAP: " << currentVWAP << ", Volume: " << executionVolume << std::endl;
        } else {
            totalNonExecutions++;
            std::cout << timestamp << " | VWAP exceeds target, no execution." << std::endl;
        }

        logger.logExecution(timestamp, currentVWAP, targetVWAP, executed);
    }

    // Get execution statistics
    void printStatistics() const {
        std::cout << "\n--- Execution Statistics ---\n";
        std::cout << "Total Executions: " << totalExecutions << std::endl;
        std::cout << "Total Non-Executions: " << totalNonExecutions << std::endl;
        std::cout << "Total Executed Volume: " << totalExecutedVolume << std::endl;
        if (totalExecutions > 0) {
            double avgExecutionPrice = std::accumulate(executionPrices.begin(), executionPrices.end(), 0.0) / totalExecutions;
            std::cout << "Average Execution Price: " << avgExecutionPrice << std::endl;
        }
    }

    // Reset VWAP calculation and execution statistics (for a new trading session)
    void reset() {
        prices.clear();
        volumes.clear();
        executionPrices.clear();
        executionVolumes.clear();
        totalVolume = 0;
        totalPriceVolume = 0;
        totalExecutions = 0;
        totalNonExecutions = 0;
        totalExecutedVolume = 0;
        std::cout << "VWAP execution reset for a new session.\n";
    }

private:
    // Determine volume to execute based on price and target
    double getExecutionVolume(double currentVWAP, double targetVWAP) const {
        // Simulate some volume calculation logic
        return std::min(1000.0, std::max(100.0, 500.0 * std::exp(-(currentVWAP - targetVWAP) / targetVWAP)));
    }
};

// Usage
int main() {
    // Initialize VWAP execution with logging enabled
    VWAPExecution vwapExec("vwap_execution_log.txt");

    // Simulated market data (price, volume)
    vwapExec.addMarketData(100.5, 150);
    vwapExec.addMarketData(101.0, 200);
    vwapExec.addMarketData(99.8, 250);
    vwapExec.addMarketData(100.2, 180);
    vwapExec.addMarketData(101.5, 130);

    // Target VWAP for execution
    double targetVWAP1 = 100.8;
    double targetVWAP2 = 101.2;

    // Execute orders at different target VWAPs
    vwapExec.executeOrder(targetVWAP1);
    vwapExec.executeOrder(targetVWAP2);

    // Print execution statistics
    vwapExec.printStatistics();

    // Reset for a new session
    vwapExec.reset();

    // Simulated market data for the new session
    vwapExec.addMarketData(102.1, 300);
    vwapExec.addMarketData(101.3, 400);
    vwapExec.addMarketData(100.8, 350);

    // Execute orders in the new session
    vwapExec.executeOrder(101.0);
    vwapExec.executeOrder(101.5);

    // Print execution statistics for the new session
    vwapExec.printStatistics();

    return 0;
}
#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>
#include <stdexcept>

// TWAP Algorithm for time-weighted average execution of large orders
class TWAPExecution {
private:
    int totalOrderSize; 
    int timeInterval;   
    int totalDuration;  
    int executedVolume; 
    std::chrono::time_point<std::chrono::steady_clock> startTime; 
    std::vector<int> orderSchedule; 

    // Validate the input parameters to ensure correct configuration
    void validateParameters() {
        if (totalOrderSize <= 0) {
            throw std::invalid_argument("Total order size must be greater than zero.");
        }
        if (timeInterval <= 0) {
            throw std::invalid_argument("Time interval must be greater than zero.");
        }
        if (totalDuration <= 0 || totalDuration < timeInterval) {
            throw std::invalid_argument("Total duration must be greater than zero and at least equal to the time interval.");
        }
    }

    // Calculate the order schedule by dividing the order into slices
    void calculateOrderSchedule() {
        int slices = totalDuration / timeInterval;
        int orderPerSlice = std::ceil(static_cast<double>(totalOrderSize) / slices);

        for (int i = 0; i < slices; i++) {
            int volume = std::min(orderPerSlice, totalOrderSize - executedVolume);
            orderSchedule.push_back(volume);
            executedVolume += volume;
        }

        // Log the calculated schedule
        logOrderSchedule();
    }

    // Log the order schedule for verification
    void logOrderSchedule() {
        std::cout << "Order Schedule: ";
        for (int i = 0; i < orderSchedule.size(); ++i) {
            std::cout << orderSchedule[i] << " ";
        }
        std::cout << std::endl;
    }

    // Method to simulate the execution of an order slice
    void executeSlice(int volume) {
        try {
            // Simulate actual execution (connecting to a broker API)
            std::cout << "Executing slice with volume: " << volume << std::endl;
            // Simulate network latency or exchange processing time
            std::this_thread::sleep_for(std::chrono::seconds(1));

            // Log successful execution
            std::cout << "Successfully executed slice of volume: " << volume << std::endl;
        } catch (const std::exception& ex) {
            // Handle any execution-related errors (network issues)
            std::cerr << "Error executing order slice: " << ex.what() << std::endl;
        }
    }

    // Check whether the total order has been executed
    bool isExecutionComplete() {
        return executedVolume >= totalOrderSize;
    }

public:
    // Constructor to initialize TWAP execution parameters
    TWAPExecution(int totalOrderSize, int timeInterval, int totalDuration)
        : totalOrderSize(totalOrderSize), timeInterval(timeInterval), totalDuration(totalDuration), executedVolume(0) {
        
        try {
            // Validate the input parameters
            validateParameters();

            // Set the start time for the execution
            startTime = std::chrono::steady_clock::now();

            // Calculate the schedule for executing the order
            calculateOrderSchedule();

        } catch (const std::invalid_argument& e) {
            std::cerr << "Initialization error: " << e.what() << std::endl;
            throw;
        }
    }

    // Method to execute the TWAP strategy
    void execute() {
        try {
            std::cout << "Starting TWAP execution..." << std::endl;

            // Iterate through the order schedule and execute each slice
            for (int volume : orderSchedule) {
                auto now = std::chrono::steady_clock::now();
                auto elapsedTime = std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count();

                if (elapsedTime < totalDuration) {
                    executeSlice(volume);

                    // Sleep for the specified time interval before next slice execution
                    std::this_thread::sleep_for(std::chrono::seconds(timeInterval));

                } else {
                    std::cout << "Total execution time exceeded. Ending execution." << std::endl;
                    break;
                }

                // Check if execution is complete
                if (isExecutionComplete()) {
                    std::cout << "TWAP execution complete. Total executed volume: " << executedVolume << std::endl;
                    break;
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "Execution error: " << e.what() << std::endl;
        }
    }

    // Method to handle any cleanup activities
    void finalize() {
        if (!isExecutionComplete()) {
            std::cout << "Finalizing TWAP execution with remaining volume: " << totalOrderSize - executedVolume << std::endl;
        } else {
            std::cout << "Execution finalized successfully." << std::endl;
        }
    }
};

int main() {
    try {
        // Initialize TWAP parameters
        int totalOrderSize = 10000; 
        int timeInterval = 5;     
        int totalDuration = 60;    

        // Create the TWAP execution object
        TWAPExecution twap(totalOrderSize, timeInterval, totalDuration);

        // Start execution of the TWAP algorithm
        twap.execute();

        // Perform any cleanup or finalization
        twap.finalize();

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
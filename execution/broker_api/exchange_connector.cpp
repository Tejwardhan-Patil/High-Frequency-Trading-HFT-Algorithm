#include <iostream>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <vector>
#include <atomic>
#include <chrono>
#include <memory>
#include <asio.hpp> 
#include "fix_connector.hpp" 
#include "websocket_connector.hpp" 

class ExchangeConnector {
public:
    ExchangeConnector(const std::string& exchange, const std::string& api_key, const std::string& secret_key)
        : exchange_name(exchange), api_key(api_key), secret_key(secret_key), is_connected(false), stop_flag(false) {}

    ~ExchangeConnector() { stop(); }

    void connect() {
        std::lock_guard<std::mutex> lock(connection_mutex);
        if (is_connected) {
            std::cout << "Already connected to " << exchange_name << std::endl;
            return;
        }
        connection_thread = std::thread([this]() { this->run(); });
        connection_cv.wait(connection_lock, [this] { return is_connected.load(); });
    }

    void disconnect() {
        std::lock_guard<std::mutex> lock(connection_mutex);
        stop_flag = true;
        if (connection_thread.joinable()) {
            connection_thread.join();
        }
        is_connected.store(false);
    }

    void send_order(const std::string& order_data) {
        if (!is_connected) {
            std::cerr << "Not connected. Cannot send order." << std::endl;
            return;
        }
        std::lock_guard<std::mutex> lock(order_mutex);
        orders.push(order_data);
    }

    void subscribe_market_data(const std::string& symbol) {
        std::lock_guard<std::mutex> lock(data_mutex);
        market_data_subscriptions.push_back(symbol);
    }

    std::string get_market_data() {
        std::lock_guard<std::mutex> lock(data_mutex);
        if (market_data.empty()) {
            return "";
        }
        std::string data = market_data.front();
        market_data.pop();
        return data;
    }

private:
    std::string exchange_name, api_key, secret_key;
    std::atomic<bool> is_connected, stop_flag;
    std::thread connection_thread;
    std::mutex connection_mutex, order_mutex, data_mutex;
    std::condition_variable connection_cv;
    std::queue<std::string> orders, market_data;
    std::vector<std::string> market_data_subscriptions;

    void run() {
        try {
            if (exchange_name == "FIX") {
                FIXConnector fix_connector(api_key, secret_key);
                fix_connector.connect();
                handle_orders_and_data(fix_connector);
            } else if (exchange_name == "WebSocket") {
                WebSocketConnector ws_connector(api_key, secret_key);
                ws_connector.connect();
                handle_orders_and_data(ws_connector);
            } else {
                throw std::runtime_error("Unknown protocol");
            }
            is_connected.store(true);
            connection_cv.notify_all();
        } catch (const std::exception& e) {
            std::cerr << "Connection failed: " << e.what() << std::endl;
            is_connected.store(false);
        }
    }

    template<typename ConnectorType>
    void handle_orders_and_data(ConnectorType& connector) {
        while (!stop_flag.load()) {
            if (!orders.empty()) {
                std::lock_guard<std::mutex> lock(order_mutex);
                std::string order = orders.front();
                orders.pop();
                connector.send_order(order);
            }

            std::string data = connector.get_market_data();
            if (!data.empty()) {
                std::lock_guard<std::mutex> lock(data_mutex);
                market_data.push(data);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        connector.disconnect();
    }

    void stop() {
        stop_flag = true;
        if (connection_thread.joinable()) {
            connection_thread.join();
        }
    }
};

// FIXConnector.cpp
class FIXConnector {
public:
    FIXConnector(const std::string& api_key, const std::string& secret_key) {
        // Initialize FIX connection
    }

    void connect() {
        std::cout << "Connecting via FIX Protocol..." << std::endl;
    }

    void disconnect() {
        std::cout << "Disconnecting FIX Protocol..." << std::endl;
    }

    void send_order(const std::string& order) {
        std::cout << "Sending order via FIX: " << order << std::endl;
    }

    std::string get_market_data() {
        return "FIX Market Data";
    }
};

// WebSocketConnector.cpp
class WebSocketConnector {
public:
    WebSocketConnector(const std::string& api_key, const std::string& secret_key) {
        // Initialize WebSocket connection
    }

    void connect() {
        std::cout << "Connecting via WebSocket..." << std::endl;
    }

    void disconnect() {
        std::cout << "Disconnecting WebSocket..." << std::endl;
    }

    void send_order(const std::string& order) {
        std::cout << "Sending order via WebSocket: " << order << std::endl;
    }

    std::string get_market_data() {
        return "WebSocket Market Data";
    }
};

// Main to demonstrate functionality
int main() {
    ExchangeConnector connector("FIX", "api_key", "secret_key");
    connector.connect();
    connector.subscribe_market_data("AAPL");
    connector.send_order("Buy 100 shares");
    
    std::this_thread::sleep_for(std::chrono::seconds(1));
    std::string market_data = connector.get_market_data();
    std::cout << "Received Market Data: " << market_data << std::endl;

    connector.disconnect();
    return 0;
}
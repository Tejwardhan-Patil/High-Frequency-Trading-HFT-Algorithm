#include <iostream>
#include <unordered_map>
#include <vector>
#include <string>
#include <mutex>
#include <chrono>
#include "exchange_connector.h"
#include "log_utils.h"

class Order {
public:
    enum class Status { PENDING, FILLED, CANCELED, REJECTED, PARTIALLY_FILLED };

    Order(int id, const std::string& symbol, double price, int quantity, bool is_buy)
        : order_id(id), symbol(symbol), price(price), quantity(quantity), is_buy(is_buy), status(Status::PENDING), filled_quantity(0),
          timestamp(std::chrono::system_clock::now()) {}

    int getOrderId() const { return order_id; }
    std::string getSymbol() const { return symbol; }
    double getPrice() const { return price; }
    int getQuantity() const { return quantity; }
    int getFilledQuantity() const { return filled_quantity; }
    bool isBuy() const { return is_buy; }
    Status getStatus() const { return status; }
    void setStatus(Status s) { status = s; }
    void updateFilledQuantity(int filled_qty) {
        filled_quantity += filled_qty;
        if (filled_quantity >= quantity) {
            status = Status::FILLED;
        } else {
            status = Status::PARTIALLY_FILLED;
        }
    }
    auto getTimestamp() const { return timestamp; }

private:
    int order_id;
    std::string symbol;
    double price;
    int quantity;
    int filled_quantity;
    bool is_buy;
    Status status;
    std::chrono::time_point<std::chrono::system_clock> timestamp;
};

class OrderManager {
public:
    OrderManager() = default;

    int createOrder(const std::string& symbol, double price, int quantity, bool is_buy) {
        std::lock_guard<std::mutex> lock(mutex_);
        int order_id = ++order_id_counter;
        orders_.emplace(order_id, Order(order_id, symbol, price, quantity, is_buy));
        logOrder("CREATE", order_id);
        exchangeConnector.sendOrder(order_id, symbol, price, quantity, is_buy);
        return order_id;
    }

    void cancelOrder(int order_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (orders_.find(order_id) != orders_.end() && orders_[order_id].getStatus() == Order::Status::PENDING) {
            orders_[order_id].setStatus(Order::Status::CANCELED);
            logOrder("CANCEL", order_id);
            exchangeConnector.cancelOrder(order_id);
        } else {
            log_utils::log("[ORDER MANAGER] Order cancel failed. Order ID: " + std::to_string(order_id) + " is not pending.");
        }
    }

    void modifyOrder(int order_id, double new_price, int new_quantity) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (orders_.find(order_id) != orders_.end() && orders_[order_id].getStatus() == Order::Status::PENDING) {
            Order& order = orders_.at(order_id);
            order = Order(order_id, order.getSymbol(), new_price, new_quantity, order.isBuy());
            logOrder("MODIFY", order_id);
            exchangeConnector.modifyOrder(order_id, new_price, new_quantity);
        } else {
            log_utils::log("[ORDER MANAGER] Order modification failed. Order ID: " + std::to_string(order_id) + " is not pending.");
        }
    }

    void processOrderUpdate(int order_id, Order::Status status, int filled_qty = 0) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (orders_.find(order_id) != orders_.end()) {
            orders_[order_id].setStatus(status);
            if (filled_qty > 0) {
                orders_[order_id].updateFilledQuantity(filled_qty);
            }
            logOrder("UPDATE", order_id);
        } else {
            log_utils::log("[ORDER MANAGER] Order update failed. Order ID: " + std::to_string(order_id) + " not found.");
        }
    }

    std::vector<Order> getActiveOrders() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<Order> active_orders;
        for (const auto& [order_id, order] : orders_) {
            if (order.getStatus() == Order::Status::PENDING || order.getStatus() == Order::Status::PARTIALLY_FILLED) {
                active_orders.push_back(order);
            }
        }
        return active_orders;
    }

    std::vector<Order> getFilledOrders() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<Order> filled_orders;
        for (const auto& [order_id, order] : orders_) {
            if (order.getStatus() == Order::Status::FILLED) {
                filled_orders.push_back(order);
            }
        }
        return filled_orders;
    }

    void printOrderSummary() {
        std::lock_guard<std::mutex> lock(mutex_);
        log_utils::log("[ORDER MANAGER] Order Summary:");
        for (const auto& [order_id, order] : orders_) {
            logOrder("SUMMARY", order_id);
        }
    }

    bool isOrderActive(int order_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (orders_.find(order_id) != orders_.end()) {
            return orders_[order_id].getStatus() == Order::Status::PENDING || orders_[order_id].getStatus() == Order::Status::PARTIALLY_FILLED;
        }
        return false;
    }

private:
    std::unordered_map<int, Order> orders_;
    std::mutex mutex_;
    int order_id_counter = 0;
    ExchangeConnector exchangeConnector;

    void logOrder(const std::string& action, int order_id) {
        const Order& order = orders_.at(order_id);
        std::string status_str;
        switch (order.getStatus()) {
            case Order::Status::PENDING: status_str = "PENDING"; break;
            case Order::Status::FILLED: status_str = "FILLED"; break;
            case Order::Status::CANCELED: status_str = "CANCELED"; break;
            case Order::Status::REJECTED: status_str = "REJECTED"; break;
            case Order::Status::PARTIALLY_FILLED: status_str = "PARTIALLY FILLED"; break;
        }
        log_utils::log("[ORDER MANAGER] Action: " + action +
                        ", Order ID: " + std::to_string(order_id) +
                        ", Symbol: " + order.getSymbol() +
                        ", Price: " + std::to_string(order.getPrice()) +
                        ", Quantity: " + std::to_string(order.getQuantity()) +
                        ", Filled Quantity: " + std::to_string(order.getFilledQuantity()) +
                        ", Status: " + status_str +
                        ", Timestamp: " + std::to_string(std::chrono::duration_cast<std::chrono::seconds>(order.getTimestamp().time_since_epoch()).count()));
    }
};

int main() {
    OrderManager orderManager;

    // Usage
    int order1 = orderManager.createOrder("AAPL", 150.5, 100, true);
    int order2 = orderManager.createOrder("GOOG", 2725.0, 50, false);

    orderManager.modifyOrder(order1, 151.0, 100);
    orderManager.processOrderUpdate(order1, Order::Status::PARTIALLY_FILLED, 50);
    orderManager.processOrderUpdate(order1, Order::Status::FILLED, 50);

    orderManager.cancelOrder(order2);
    orderManager.printOrderSummary();

    return 0;
}
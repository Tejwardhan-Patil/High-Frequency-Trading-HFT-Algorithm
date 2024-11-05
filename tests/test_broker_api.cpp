#include <iostream>
#include <cassert>
#include <chrono>
#include <thread>
#include "execution/broker_api/exchange_connector.cpp"

void log_test_result(const std::string& test_name, bool passed) {
    if (passed) {
        std::cout << test_name << ": Passed" << std::endl;
    } else {
        std::cerr << test_name << ": Failed" << std::endl;
    }
}

void test_connection_establishment() {
    std::cout << "Running test: Connection Establishment" << std::endl;
    ExchangeConnector connector;
    bool connection_status = connector.establishConnection("https://api.website.com");
    
    log_test_result("Connection Establishment", connection_status);
    assert(connection_status == true && "Connection should be established successfully");

    bool invalid_connection = connector.establishConnection("invalid_url");
    log_test_result("Invalid URL Connection", !invalid_connection);
    assert(invalid_connection == false && "Invalid URL should not establish connection");
}

void test_reconnection_logic() {
    std::cout << "Running test: Reconnection Logic" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    bool disconnected = connector.disconnect();
    assert(disconnected == true && "Disconnection should be successful");
    
    bool reconnection_status = connector.reconnect();
    log_test_result("Reconnection after disconnect", reconnection_status);
    assert(reconnection_status == true && "Reconnection should be successful after disconnection");
}

void test_order_execution() {
    std::cout << "Running test: Order Execution" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    Order order;
    order.type = OrderType::LIMIT;
    order.symbol = "AAPL";
    order.quantity = 100;
    order.price = 150.25;

    bool execution_status = connector.executeOrder(order);
    log_test_result("Order Execution", execution_status);
    assert(execution_status == true && "Order execution should be successful");

    order.type = OrderType::MARKET;
    bool market_order_status = connector.executeOrder(order);
    log_test_result("Market Order Execution", market_order_status);
    assert(market_order_status == true && "Market order execution should be successful");
}

void test_order_execution_with_invalid_order() {
    std::cout << "Running test: Invalid Order Execution" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    Order invalid_order;
    invalid_order.type = OrderType::LIMIT;
    invalid_order.symbol = ""; // Invalid symbol
    invalid_order.quantity = 0; // Invalid quantity
    invalid_order.price = -100.0; // Invalid price

    bool invalid_execution_status = connector.executeOrder(invalid_order);
    log_test_result("Invalid Order Execution", !invalid_execution_status);
    assert(invalid_execution_status == false && "Invalid order execution should fail");
}

void test_order_cancellation() {
    std::cout << "Running test: Order Cancellation" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    Order order;
    order.id = 12345;
    bool cancel_status = connector.cancelOrder(order);
    log_test_result("Order Cancellation", cancel_status);
    assert(cancel_status == true && "Order cancellation should be successful");

    order.id = 54321; // Non-existent order
    bool invalid_cancel_status = connector.cancelOrder(order);
    log_test_result("Non-existent Order Cancellation", !invalid_cancel_status);
    assert(invalid_cancel_status == false && "Cancellation of non-existent order should fail");
}

void test_order_status_update() {
    std::cout << "Running test: Order Status Update" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    Order order;
    order.id = 12345;
    OrderStatus status = connector.getOrderStatus(order);
    log_test_result("Order Status Update", status == OrderStatus::FILLED);
    assert(status == OrderStatus::FILLED && "Order status should be FILLED");

    order.id = 67890; // Non-existent order
    OrderStatus invalid_status = connector.getOrderStatus(order);
    log_test_result("Non-existent Order Status", invalid_status == OrderStatus::UNKNOWN);
    assert(invalid_status == OrderStatus::UNKNOWN && "Status of non-existent order should be UNKNOWN");
}

void test_bulk_order_execution() {
    std::cout << "Running test: Bulk Order Execution" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    for (int i = 0; i < 10; i++) {
        Order order;
        order.type = OrderType::LIMIT;
        order.symbol = "AAPL";
        order.quantity = 10 + i;
        order.price = 150.25 + i;

        bool execution_status = connector.executeOrder(order);
        log_test_result("Bulk Order Execution " + std::to_string(i+1), execution_status);
        assert(execution_status == true && "Bulk order execution should be successful");
    }
}

void test_timeout_handling() {
    std::cout << "Running test: Timeout Handling" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    connector.setTimeout(5000); // Set timeout to 5 seconds
    bool execution_status = connector.executeOrder(Order()); // Send a basic order to test timeout
    log_test_result("Order Execution with Timeout", execution_status);
    
    assert(execution_status == true && "Order execution should complete within timeout");
    
    std::this_thread::sleep_for(std::chrono::milliseconds(6000)); // Simulate delay
    bool delayed_execution_status = connector.executeOrder(Order()); // Test after delay
    
    log_test_result("Delayed Order Execution", !delayed_execution_status);
    assert(delayed_execution_status == false && "Order execution should fail after timeout");
}

void test_order_amendment() {
    std::cout << "Running test: Order Amendment" << std::endl;
    ExchangeConnector connector;
    connector.establishConnection("https://api.website.com");

    Order order;
    order.id = 12345;
    order.quantity = 200; // Amend order quantity

    bool amendment_status = connector.amendOrder(order);
    log_test_result("Order Amendment", amendment_status);
    assert(amendment_status == true && "Order amendment should be successful");

    Order invalid_order;
    invalid_order.id = 54321; // Non-existent order
    bool invalid_amendment_status = connector.amendOrder(invalid_order);
    log_test_result("Invalid Order Amendment", !invalid_amendment_status);
    assert(invalid_amendment_status == false && "Amendment of non-existent order should fail");
}

void test_failed_connection_recovery() {
    std::cout << "Running test: Failed Connection Recovery" << std::endl;
    ExchangeConnector connector;
    
    // Simulate failed connection
    bool connection_status = connector.establishConnection("invalid_url");
    assert(connection_status == false && "Connection should fail with invalid URL");
    
    // Attempt recovery
    bool recovery_status = connector.reconnect();
    log_test_result("Recovery after failed connection", !recovery_status);
    assert(recovery_status == false && "Recovery should fail after invalid connection attempt");

    // Now connect to the correct URL
    connection_status = connector.establishConnection("https://api.website.com");
    assert(connection_status == true && "Recovery should succeed after connecting to valid URL");
}

int main() {
    test_connection_establishment();
    test_reconnection_logic();
    test_order_execution();
    test_order_execution_with_invalid_order();
    test_order_cancellation();
    test_order_status_update();
    test_bulk_order_execution();
    test_timeout_handling();
    test_order_amendment();
    test_failed_connection_recovery();

    std::cout << "All broker API tests passed successfully!" << std::endl;
    return 0;
}
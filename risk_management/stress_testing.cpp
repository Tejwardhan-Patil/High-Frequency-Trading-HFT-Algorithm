#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
#include <chrono>
#include <string>

class MarketCondition {
public:
    double price_change_percentage;
    double volatility;
    double liquidity;

    MarketCondition(double price_change, double vol, double liq)
        : price_change_percentage(price_change), volatility(vol), liquidity(liq) {}
};

class Asset {
public:
    std::string name;
    double initial_value;
    double position_size;

    Asset(std::string asset_name, double asset_value, double position)
        : name(asset_name), initial_value(asset_value), position_size(position) {}
};

class Portfolio {
public:
    std::vector<Asset> assets;

    void add_asset(const std::string& name, double value, double position) {
        assets.emplace_back(name, value, position);
    }

    double get_total_value() const {
        double total = 0.0;
        for (const auto& asset : assets) {
            total += asset.initial_value * asset.position_size;
        }
        return total;
    }
};

class StressTest {
private:
    Portfolio portfolio;
    std::vector<MarketCondition> scenarios;
    std::vector<double> portfolio_values;
    std::vector<double> drawdowns;
    std::vector<double> volatility_impacts;

    double simulate_asset_value(const Asset& asset, double price_change_percentage, double volatility, double liquidity) {
        // Model asset value with price change, volatility, and liquidity
        double shock = price_change_percentage + volatility * (rand() % 100) / 100.0;
        double liquidity_factor = 1.0 - std::min(std::max(0.0, liquidity), 1.0); // Liquidity: 0 (no liquidity) to 1 (full liquidity)
        return asset.initial_value * (1 + shock * liquidity_factor) * asset.position_size;
    }

    double simulate_portfolio_value(double price_change_percentage, double volatility, double liquidity) {
        // Simulate the value of the entire portfolio under stress
        double portfolio_value = 0.0;
        for (const auto& asset : portfolio.assets) {
            portfolio_value += simulate_asset_value(asset, price_change_percentage, volatility, liquidity);
        }
        return portfolio_value;
    }

    double calculate_drawdown(double initial_value, double new_value) {
        return (initial_value - new_value) / initial_value * 100;
    }

    double calculate_volatility_impact(double volatility) {
        return volatility * 100; // Impact percentage of volatility
    }

public:
    StressTest(const Portfolio& port)
        : portfolio(port) {}

    void add_scenario(double price_change_percentage, double volatility, double liquidity) {
        scenarios.emplace_back(price_change_percentage, volatility, liquidity);
    }

    void run_tests() {
        portfolio_values.clear();
        drawdowns.clear();
        volatility_impacts.clear();
        double initial_value = portfolio.get_total_value();

        for (const auto& scenario : scenarios) {
            double new_value = simulate_portfolio_value(scenario.price_change_percentage, scenario.volatility, scenario.liquidity);
            portfolio_values.push_back(new_value);

            double drawdown = calculate_drawdown(initial_value, new_value);
            drawdowns.push_back(drawdown);

            double vol_impact = calculate_volatility_impact(scenario.volatility);
            volatility_impacts.push_back(vol_impact);
        }
    }

    void generate_report() const {
        std::cout << "Stress Test Report\n";
        std::cout << "Initial Portfolio Value: " << portfolio.get_total_value() << "\n";
        std::cout << "-----------------------------------------\n";

        for (size_t i = 0; i < scenarios.size(); ++i) {
            const auto& scenario = scenarios[i];
            std::cout << "Scenario " << i + 1 << ":\n";
            std::cout << " - Price Change: " << scenario.price_change_percentage * 100 << "%\n";
            std::cout << " - Volatility: " << scenario.volatility * 100 << "%\n";
            std::cout << " - Liquidity: " << scenario.liquidity * 100 << "%\n";
            std::cout << " - Portfolio Value: " << portfolio_values[i] << "\n";
            std::cout << " - Drawdown: " << drawdowns[i] << "%\n";
            std::cout << " - Volatility Impact: " << volatility_impacts[i] << "%\n";
            std::cout << "-----------------------------------------\n";
        }
    }
};

int main() {
    srand(static_cast<unsigned>(std::chrono::system_clock::now().time_since_epoch().count()));

    Portfolio portfolio;
    portfolio.add_asset("Stock A", 500000, 1.0);  // Asset name, value, position size
    portfolio.add_asset("Bond B", 300000, 1.0);
    portfolio.add_asset("Commodity C", 200000, 1.0);

    StressTest stress_test(portfolio);

    // Add various market conditions for stress testing
    stress_test.add_scenario(-0.05, 0.02, 0.8);  // 5% drop in price, 2% volatility, 80% liquidity
    stress_test.add_scenario(0.1, 0.05, 0.5);    // 10% price increase, 5% volatility, 50% liquidity
    stress_test.add_scenario(-0.2, 0.1, 0.3);    // 20% drop in price, 10% volatility, 30% liquidity
    stress_test.add_scenario(0.3, 0.15, 0.7);    // 30% price increase, 15% volatility, 70% liquidity
    stress_test.add_scenario(-0.1, 0.08, 0.4);   // 10% drop in price, 8% volatility, 40% liquidity

    // Run stress tests
    stress_test.run_tests();

    // Generate report
    stress_test.generate_report();

    return 0;
}
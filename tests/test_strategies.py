import unittest
import momentum_strategy  # SWIG-wrapped C++ momentum strategy
from py4j.java_gateway import JavaGateway  # Py4J for Java strategies
from strategies.mean_reversion.mean_reversion_strategy import MeanReversionStrategy  
from strategies.backtest import Backtest  
from strategies.optimize import Optimizer  
from data.processed.aggregated_data import AggregatedData  

class TestTradingStrategies(unittest.TestCase):

    def setUp(self):
        # Initial setup for the test cases
        self.data = AggregatedData.load_data('processed/aggregated_data/sample_data.csv')
        
        # C++ momentum strategy via SWIG
        self.momentum_strategy = momentum_strategy.MomentumStrategy()
        
        # Mean reversion strategy (Python)
        self.mean_reversion_strategy = MeanReversionStrategy()

        # Set up Java Gateway for Java strategies (Statistical Arbitrage, Market Making)
        self.gateway = JavaGateway()  # Start a Py4J gateway
        self.stat_arbitrage_strategy = self.gateway.entry_point.getStatisticalArbitrageStrategy()
        self.market_making_strategy = self.gateway.entry_point.getMarketMakingStrategy()

        # Backtest and Optimizer (Python)
        self.backtest = Backtest()
        self.optimizer = Optimizer()

    def tearDown(self):
        # Clean up any persistent objects
        del self.data
        del self.momentum_strategy
        del self.mean_reversion_strategy
        del self.stat_arbitrage_strategy
        del self.market_making_strategy
        del self.backtest
        del self.optimizer

    def test_momentum_strategy(self):
        # Testing the momentum strategy logic (C++)
        try:
            result = self.momentum_strategy.run(self.data)  # C++ method call
            self.assertIsNotNone(result)
            self.assertTrue(result['profit'] >= 0, "Momentum Strategy did not yield positive results")
            self.assertIn('trades', result, "Momentum Strategy missing 'trades' in results")
            self.assertGreater(len(result['trades']), 0, "No trades executed in Momentum Strategy")
        except Exception as e:
            self.fail(f"Momentum Strategy failed with error: {str(e)}")

    def test_mean_reversion_strategy(self):
        # Testing the mean reversion strategy logic (Python)
        try:
            result = self.mean_reversion_strategy.run(self.data)
            self.assertIsNotNone(result)
            self.assertTrue(result['profit'] >= 0, "Mean Reversion Strategy did not yield positive results")
            self.assertIn('signals', result, "Mean Reversion Strategy missing 'signals' in results")
            self.assertGreaterEqual(result['signals'], 1, "Mean Reversion Strategy did not generate signals")
        except Exception as e:
            self.fail(f"Mean Reversion Strategy failed with error: {str(e)}")

    def test_statistical_arbitrage_strategy(self):
        # Testing the statistical arbitrage strategy logic (Java)
        try:
            result = self.stat_arbitrage_strategy.run(self.data)  # Py4J call to Java method
            self.assertIsNotNone(result)
            self.assertTrue(result['profit'] >= 0, "Statistical Arbitrage Strategy did not yield positive results")
            self.assertIn('opportunities', result, "Statistical Arbitrage Strategy missing 'opportunities'")
            self.assertGreaterEqual(len(result['opportunities']), 1, "No arbitrage opportunities found")
        except Exception as e:
            self.fail(f"Statistical Arbitrage Strategy failed with error: {str(e)}")

    def test_market_making_strategy(self):
        # Testing the market making strategy logic (Java)
        try:
            result = self.market_making_strategy.run(self.data)  # Py4J call to Java method
            self.assertIsNotNone(result)
            self.assertTrue(result['profit'] >= 0, "Market Making Strategy did not yield positive results")
            self.assertIn('limit_orders', result, "Market Making Strategy missing 'limit_orders'")
            self.assertGreater(len(result['limit_orders']), 0, "No limit orders placed in Market Making Strategy")
        except Exception as e:
            self.fail(f"Market Making Strategy failed with error: {str(e)}")

    def test_backtest_momentum_strategy(self):
        # Backtesting momentum strategy
        try:
            result = self.backtest.run(self.data, [self.momentum_strategy])
            self.assertIsNotNone(result)
            self.assertTrue(result['overall_profit'] >= 0, "Momentum Strategy Backtest did not yield positive overall results")
        except Exception as e:
            self.fail(f"Backtest for Momentum Strategy failed with error: {str(e)}")

    def test_backtest_mean_reversion_strategy(self):
        # Backtesting mean reversion strategy
        try:
            result = self.backtest.run(self.data, [self.mean_reversion_strategy])
            self.assertIsNotNone(result)
            self.assertTrue(result['overall_profit'] >= 0, "Mean Reversion Strategy Backtest did not yield positive overall results")
        except Exception as e:
            self.fail(f"Backtest for Mean Reversion Strategy failed with error: {str(e)}")

    def test_backtest_statistical_arbitrage_strategy(self):
        # Backtesting statistical arbitrage strategy (Java)
        try:
            result = self.backtest.run(self.data, [self.stat_arbitrage_strategy])
            self.assertIsNotNone(result)
            self.assertTrue(result['overall_profit'] >= 0, "Statistical Arbitrage Strategy Backtest did not yield positive overall results")
        except Exception as e:
            self.fail(f"Backtest for Statistical Arbitrage Strategy failed with error: {str(e)}")

    def test_backtest_market_making_strategy(self):
        # Backtesting market making strategy (Java)
        try:
            result = self.backtest.run(self.data, [self.market_making_strategy])
            self.assertIsNotNone(result)
            self.assertTrue(result['overall_profit'] >= 0, "Market Making Strategy Backtest did not yield positive overall results")
        except Exception as e:
            self.fail(f"Backtest for Market Making Strategy failed with error: {str(e)}")

    def test_optimization_momentum_strategy(self):
        # Optimizing momentum strategy's parameters
        try:
            optimized_params = self.optimizer.optimize(self.data, self.momentum_strategy)
            self.assertIsNotNone(optimized_params)
            self.assertIn('best_parameters', optimized_params, "Optimization did not return expected parameters")
            self.assertTrue(len(optimized_params['best_parameters']) > 0, "Optimization did not yield valid parameters")
        except Exception as e:
            self.fail(f"Optimization for Momentum Strategy failed with error: {str(e)}")

    def test_optimization_mean_reversion_strategy(self):
        # Optimizing mean reversion strategy's parameters
        try:
            optimized_params = self.optimizer.optimize(self.data, self.mean_reversion_strategy)
            self.assertIsNotNone(optimized_params)
            self.assertIn('best_parameters', optimized_params, "Optimization did not return expected parameters")
            self.assertTrue(len(optimized_params['best_parameters']) > 0, "Optimization did not yield valid parameters")
        except Exception as e:
            self.fail(f"Optimization for Mean Reversion Strategy failed with error: {str(e)}")

    def test_optimization_statistical_arbitrage_strategy(self):
        # Optimizing statistical arbitrage strategy's parameters (Java)
        try:
            optimized_params = self.optimizer.optimize(self.data, self.stat_arbitrage_strategy)
            self.assertIsNotNone(optimized_params)
            self.assertIn('best_parameters', optimized_params, "Optimization did not return expected parameters")
            self.assertTrue(len(optimized_params['best_parameters']) > 0, "Optimization did not yield valid parameters")
        except Exception as e:
            self.fail(f"Optimization for Statistical Arbitrage Strategy failed with error: {str(e)}")

    def test_optimization_market_making_strategy(self):
        # Optimizing market making strategy's parameters (Java)
        try:
            optimized_params = self.optimizer.optimize(self.data, self.market_making_strategy)
            self.assertIsNotNone(optimized_params)
            self.assertIn('best_parameters', optimized_params, "Optimization did not return expected parameters")
            self.assertTrue(len(optimized_params['best_parameters']) > 0, "Optimization did not yield valid parameters")
        except Exception as e:
            self.fail(f"Optimization for Market Making Strategy failed with error: {str(e)}")

if __name__ == '__main__':
    unittest.main()
package strategies.arbitrage;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

public class StatisticalArbitrage {
    
    // Parameters for the strategy
    private double entryThreshold;
    private double exitThreshold;
    private int lookbackPeriod;
    private double hedgeRatio;

    // Constructor
    public StatisticalArbitrage(double entryThreshold, double exitThreshold, int lookbackPeriod) {
        this.entryThreshold = entryThreshold;
        this.exitThreshold = exitThreshold;
        this.lookbackPeriod = lookbackPeriod;
        this.hedgeRatio = 1.0;
    }

    // Set the hedge ratio
    public void setHedgeRatio(double hedgeRatio) {
        this.hedgeRatio = hedgeRatio;
    }

    // Calculate spread between two assets based on historical prices
    private List<Double> calculateSpread(List<Double> asset1Prices, List<Double> asset2Prices) {
        List<Double> spread = new ArrayList<>();
        for (int i = 0; i < asset1Prices.size(); i++) {
            spread.add(asset1Prices.get(i) - hedgeRatio * asset2Prices.get(i));
        }
        return spread;
    }

    // Mean of a series
    private double mean(List<Double> data) {
        double sum = 0.0;
        for (double d : data) {
            sum += d;
        }
        return sum / data.size();
    }

    // Standard deviation of a series
    private double stddev(List<Double> data, double mean) {
        double sum = 0.0;
        for (double d : data) {
            sum += Math.pow(d - mean, 2);
        }
        return Math.sqrt(sum / data.size());
    }

    // Calculate Z-score of the current spread
    private double calculateZScore(double currentSpread, double mean, double stddev) {
        if (stddev == 0.0) {
            return 0.0;
        }
        return (currentSpread - mean) / stddev;
    }

    // Identify trading signals based on Z-score
    private List<String> identifySignals(List<Double> spread) {
        List<String> signals = new ArrayList<>();
        for (int i = lookbackPeriod; i < spread.size(); i++) {
            List<Double> window = spread.subList(i - lookbackPeriod, i);
            double windowMean = mean(window);
            double windowStddev = stddev(window, windowMean);
            double zScore = calculateZScore(spread.get(i), windowMean, windowStddev);

            if (zScore > entryThreshold) {
                signals.add("Short");
            } else if (zScore < -entryThreshold) {
                signals.add("Long");
            } else if (Math.abs(zScore) < exitThreshold) {
                signals.add("Exit");
            } else {
                signals.add("Hold");
            }
        }
        return signals;
    }

    // Simulate strategy on historical data
    public Map<String, Double> simulate(List<Double> asset1Prices, List<Double> asset2Prices) {
        List<Double> spread = calculateSpread(asset1Prices, asset2Prices);
        List<String> signals = identifySignals(spread);
        double pnl = 0.0;
        double position = 0.0;
    
        for (int i = lookbackPeriod; i < signals.size(); i++) {
            String signal = signals.get(i);
            if (signal.equals("Long")) {
                position = 1.0;
            } else if (signal.equals("Short")) {
                position = -1.0;
            } else if (signal.equals("Exit")) {
                position = 0.0;
            }
            
            // PnL calculation
            if (position == 1.0) {
                pnl += asset1Prices.get(i) - asset1Prices.get(i - 1);
            } else if (position == -1.0) {
                pnl += asset2Prices.get(i - 1) - asset2Prices.get(i);
            }
        }
    
        Map<String, Double> result = new HashMap<>();
        result.put("PnL", pnl);
        return result;
    }    

    // Helper function to generate data
    private List<Double> generatePriceSeries(double startPrice, int length, double volatility) {
        List<Double> prices = new ArrayList<>();
        prices.add(startPrice);
        for (int i = 1; i < length; i++) {
            double randomShock = (Math.random() - 0.5) * volatility;
            prices.add(prices.get(i - 1) + randomShock);
        }
        return prices;
    }

    // Generate data for both assets
    public Map<String, List<Double>> generateData(int length) {
        List<Double> asset1Prices = generatePriceSeries(100.0, length, 1.5);
        List<Double> asset2Prices = generatePriceSeries(98.0, length, 1.2);
        
        Map<String, List<Double>> data = new HashMap<>();
        data.put("Asset1", asset1Prices);
        data.put("Asset2", asset2Prices);

        return data;
    }

    // Main method for testing
    public static void main(String[] args) {
        // Create a statistical arbitrage instance
        StatisticalArbitrage strategy = new StatisticalArbitrage(2.0, 0.5, 20);
        
        // Generate data
        Map<String, List<Double>> Data = strategy.generateData(1000);
        
        // Simulate the strategy
        Map<String, Double> result = strategy.simulate(
                Data.get("Asset1"),
                Data.get("Asset2")
        );
        
        // Print the profit and loss
        System.out.println("PnL: " + result.get("PnL"));
    }

    // Adjusts the hedge ratio dynamically based on asset price correlation
    public void adjustHedgeRatio(List<Double> asset1Prices, List<Double> asset2Prices) {
        double sumAsset1 = 0.0;
        double sumAsset2 = 0.0;
        double sumProduct = 0.0;
        double sumSquaredAsset1 = 0.0;

        int length = asset1Prices.size();
        for (int i = 0; i < length; i++) {
            double price1 = asset1Prices.get(i);
            double price2 = asset2Prices.get(i);

            sumAsset1 += price1;
            sumAsset2 += price2;
            sumProduct += price1 * price2;
            sumSquaredAsset1 += price1 * price1;
        }

        double numerator = (length * sumProduct) - (sumAsset1 * sumAsset2);
        double denominator = (length * sumSquaredAsset1) - (sumAsset1 * sumAsset1);

        if (denominator != 0.0) {
            hedgeRatio = numerator / denominator;
        }
    }

    // Enhanced simulation method with dynamic hedge ratio adjustment
    public Map<String, Double> simulateWithDynamicHedgeRatio(List<Double> asset1Prices, List<Double> asset2Prices) {
        adjustHedgeRatio(asset1Prices, asset2Prices);
        List<Double> spread = calculateSpread(asset1Prices, asset2Prices);
        List<String> signals = identifySignals(spread);
        double pnl = 0.0;
        double position = 0.0;

        for (int i = lookbackPeriod; i < signals.size(); i++) {
            String signal = signals.get(i);
            if (signal.equals("Long")) {
                position = 1.0;
                pnl += position * (asset1Prices.get(i) - asset1Prices.get(i - 1));
            } else if (signal.equals("Short")) {
                position = -1.0;
                pnl += position * (asset2Prices.get(i - 1) - asset2Prices.get(i));
            } else if (signal.equals("Exit")) {
                position = 0.0;
            }
        }        

        Map<String, Double> result = new HashMap<>();
        result.put("PnL", pnl);
        result.put("Final Hedge Ratio", hedgeRatio);
        return result;
    }

    // Function to calculate correlation between two assets
    private double calculateCorrelation(List<Double> asset1Prices, List<Double> asset2Prices) {
        double mean1 = mean(asset1Prices);
        double mean2 = mean(asset2Prices);

        double sumNumerator = 0.0;
        double sumSquaredDev1 = 0.0;
        double sumSquaredDev2 = 0.0;

        for (int i = 0; i < asset1Prices.size(); i++) {
            double deviation1 = asset1Prices.get(i) - mean1;
            double deviation2 = asset2Prices.get(i) - mean2;
            sumNumerator += deviation1 * deviation2;
            sumSquaredDev1 += deviation1 * deviation1;
            sumSquaredDev2 += deviation2 * deviation2;
        }

        double denominator = Math.sqrt(sumSquaredDev1 * sumSquaredDev2);
        if (denominator == 0.0) {
            return 0.0;
        }
        return sumNumerator / denominator;
    }

    // Adjusts entry and exit thresholds dynamically based on asset correlation
    public void adjustThresholdsBasedOnCorrelation(List<Double> asset1Prices, List<Double> asset2Prices) {
        double correlation = calculateCorrelation(asset1Prices, asset2Prices);
        
        if (correlation > 0.9) {
            entryThreshold = 2.5;
            exitThreshold = 0.75;
        } else if (correlation > 0.7) {
            entryThreshold = 2.0;
            exitThreshold = 0.5;
        } else {
            entryThreshold = 1.5;
            exitThreshold = 0.25;
        }
    }

    // Simulate strategy with correlation-based dynamic thresholds
    public Map<String, Double> simulateWithDynamicThresholds(List<Double> asset1Prices, List<Double> asset2Prices) {
        adjustThresholdsBasedOnCorrelation(asset1Prices, asset2Prices);
        List<Double> spread = calculateSpread(asset1Prices, asset2Prices);
        List<String> signals = identifySignals(spread);
        double pnl = 0.0;
        double position = 0.0;
    
        for (int i = lookbackPeriod; i < signals.size(); i++) {
            String signal = signals.get(i);
    
            if (signal.equals("Long")) {
                position = 1.0;
            } else if (signal.equals("Short")) {
                position = -1.0;
            } else if (signal.equals("Exit")) {
                position = 0.0;
            }
    
            // PnL calculation
            if (position == 1.0) {
                pnl += asset1Prices.get(i) - asset1Prices.get(i - 1);
            } else if (position == -1.0) {
                pnl += asset2Prices.get(i - 1) - asset2Prices.get(i);
            }
        }
    
        Map<String, Double> result = new HashMap<>();
        result.put("PnL", pnl);
        return result;
    }    

    // Full simulation including dynamic hedge ratio and dynamic thresholds
    public Map<String, Double> simulateWithDynamicStrategies(List<Double> asset1Prices, List<Double> asset2Prices) {
        adjustHedgeRatio(asset1Prices, asset2Prices);
        adjustThresholdsBasedOnCorrelation(asset1Prices, asset2Prices);
        List<Double> spread = calculateSpread(asset1Prices, asset2Prices);
        List<String> signals = identifySignals(spread);
        double pnl = 0.0;
        double position = 0.0;
    
        for (int i = lookbackPeriod; i < signals.size(); i++) {
            String signal = signals.get(i);
    
            if (signal.equals("Long")) {
                position = 1.0;
            } else if (signal.equals("Short")) {
                position = -1.0;
            } else if (signal.equals("Exit")) {
                position = 0.0;
            }
    
            // PnL calculation
            if (position == 1.0) {
                pnl += asset1Prices.get(i) - asset1Prices.get(i - 1);
            } else if (position == -1.0) {
                pnl += asset2Prices.get(i - 1) - asset2Prices.get(i);
            }
        }
    
        Map<String, Double> result = new HashMap<>();
        result.put("PnL", pnl);
        result.put("Final Hedge Ratio", hedgeRatio);
        result.put("Entry Threshold", entryThreshold);
        result.put("Exit Threshold", exitThreshold);
        return result;
    }    

    // Simulate multiple runs with random data and dynamic strategies
    public void runMultipleSimulations(int runs) {
        for (int i = 0; i < runs; i++) {
            Map<String, List<Double>> data = generateData(1000);
            Map<String, Double> result = simulateWithDynamicStrategies(
                data.get("Asset1"),
                data.get("Asset2")
            );

            System.out.println("Simulation " + (i + 1) + ":");
            System.out.println("PnL: " + result.get("PnL"));
            System.out.println("Final Hedge Ratio: " + result.get("Final Hedge Ratio"));
            System.out.println("Entry Threshold: " + result.get("Entry Threshold"));
            System.out.println("Exit Threshold: " + result.get("Exit Threshold"));
            System.out.println("-------------------------------");
        }
    }
}
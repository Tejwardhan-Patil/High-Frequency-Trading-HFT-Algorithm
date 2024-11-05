package strategies.market_making;

import java.util.Random;
import java.util.concurrent.atomic.AtomicBoolean;

public class MarketMakingStrategy {

    private double midPrice;
    private double spread;
    private double volatility;
    private double inventoryRiskAdjustment;
    private double inventoryPosition;
    private final double maxInventory;
    private final double baseSpread;
    private final AtomicBoolean running;
    private final Random randomGenerator;
    
    // Parameters for risk management
    private double maxSpread;
    private double minSpread;
    private double maxLoss;
    private double maxDailyVolume;
    private double dailyVolume;
    private double lossThreshold;

    public MarketMakingStrategy(double baseSpread, double maxInventory) {
        this.baseSpread = baseSpread;
        this.spread = baseSpread;
        this.maxInventory = maxInventory;
        this.running = new AtomicBoolean(false);
        this.randomGenerator = new Random();
        this.maxSpread = 1.0;  
        this.minSpread = 0.01; 
        this.maxLoss = 500.0;  
        this.maxDailyVolume = 10000.0; 
        this.dailyVolume = 0.0;
        this.lossThreshold = 0.0;
    }

    public void start() {
        running.set(true);
        while (running.get()) {
            updateMarketData();
            if (checkRiskLimits()) {
                adjustSpreadForVolatility();
                adjustSpreadForInventoryRisk();
                placeOrders();
                trackDailyVolume();
            } else {
                stop();
                System.out.println("Trading stopped due to risk limits being breached.");
            }
            sleep();
        }
    }

    public void stop() {
        running.set(false);
    }

    private void updateMarketData() {
        // Market data feed
        midPrice = 100 + randomGenerator.nextDouble() * 2; 
        volatility = randomGenerator.nextDouble() * 0.5;  
    }

    private void adjustSpreadForVolatility() {
        // Widen the spread during periods of high volatility
        spread = baseSpread + volatility;
        if (spread > maxSpread) {
            spread = maxSpread;
        } else if (spread < minSpread) {
            spread = minSpread;
        }
    }

    private void adjustSpreadForInventoryRisk() {
        // Inventory risk adjustment factor based on position
        inventoryRiskAdjustment = (inventoryPosition / maxInventory) * 0.5;
        spread += inventoryRiskAdjustment;
        if (spread > maxSpread) {
            spread = maxSpread;
        } else if (spread < minSpread) {
            spread = minSpread;
        }
    }

    private void placeOrders() { 
        double bidPrice = midPrice - (spread / 2);
        double askPrice = midPrice + (spread / 2);
    
        // Submit limit orders to buy and sell
        submitOrder("BUY", bidPrice);
        submitOrder("SELL", askPrice);
        
        // Simulate whether these orders are filled
        simulateOrderFill("BUY", bidPrice);
        simulateOrderFill("SELL", askPrice);
    }    

    private void submitOrder(String side, double price) {
        // Order submission
        System.out.println("Submitting " + side + " order at price: " + price);
        
        // Inventory change on order fill
        if (side.equals("BUY")) {
            inventoryPosition += randomGenerator.nextDouble();
        } else if (side.equals("SELL")) {
            inventoryPosition -= randomGenerator.nextDouble();
        }

        // Ensure inventory is within bounds
        if (inventoryPosition > maxInventory) {
            inventoryPosition = maxInventory;
        } else if (inventoryPosition < -maxInventory) {
            inventoryPosition = -maxInventory;
        }
    }

    private void trackDailyVolume() {
        // Daily trading volume tracking
        double tradeVolume = randomGenerator.nextDouble() * 100;
        dailyVolume += tradeVolume;
        System.out.println("Today's trading volume: " + dailyVolume);
    }

    private boolean checkRiskLimits() {
        // Checking for risk limits
        double currentLoss = randomGenerator.nextDouble() * 100; 
        lossThreshold += currentLoss;
        
        // Stop trading if loss exceeds the maximum loss limit
        if (lossThreshold >= maxLoss) {
            System.out.println("Max loss threshold breached.");
            return false;
        }

        // Stop trading if daily volume exceeds the limit
        if (dailyVolume >= maxDailyVolume) {
            System.out.println("Max daily volume threshold breached.");
            return false;
        }

        return true;
    }

    private void sleep() {
        // Simulate waiting for the next market tick
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.out.println("Market Making Strategy interrupted.");
        }
    }

    public static void main(String[] args) {
        double initialSpread = 0.05;
        double maxPosition = 10.0;

        MarketMakingStrategy strategy = new MarketMakingStrategy(initialSpread, maxPosition);
        strategy.start();
    }

    // Method to calculate the current position risk
    private double calculatePositionRisk() {
        // The closer the position is to the max inventory, the higher the risk
        return Math.abs(inventoryPosition / maxInventory);
    }

    // Dynamic inventory adjustment based on position risk
    private void adjustInventoryBasedOnRisk() {
        double positionRisk = calculatePositionRisk();
        
        // Adjust spread dynamically based on position risk
        if (positionRisk > 0.7) {
            // If risk is high, increase spread significantly to discourage further accumulation
            spread += (positionRisk * 0.5);
            System.out.println("Position risk is high. Increasing spread to: " + spread);
        } else if (positionRisk < 0.3) {
            // If risk is low, decrease spread to capture more market share
            spread -= (positionRisk * 0.2);
            System.out.println("Position risk is low. Reducing spread to: " + spread);
        }
        
        // Ensure spread remains within the defined boundaries
        if (spread > maxSpread) {
            spread = maxSpread;
        } else if (spread < minSpread) {
            spread = minSpread;
        }
    }

    // Method to monitor and adjust trading frequency based on market conditions
    private void adjustTradingFrequency() {
        double marketVolatility = volatility; // Using volatility as a proxy for market conditions

        if (marketVolatility > 0.4) {
            // Reduce trading frequency during high volatility to mitigate risk
            System.out.println("High market volatility. Slowing down trading frequency.");
            try {
                Thread.sleep(2000); // Increase sleep time to slow trading
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                System.out.println("Trading frequency adjustment interrupted.");
            }
        } else {
            // Maintain regular trading frequency in normal market conditions
            sleep();
        }
    }

    // Method to monitor profit and loss (PnL)
    private double calculatePnL() {
        double realizedPnL = randomGenerator.nextDouble() * 100;  
        double unrealizedPnL = inventoryPosition * midPrice; 
        
        double totalPnL = realizedPnL + unrealizedPnL;
        System.out.println("Realized PnL: " + realizedPnL + ", Unrealized PnL: " + unrealizedPnL);
        return totalPnL;
    }

    // Monitor PnL and adjust the strategy accordingly
    private void managePnL() {
        double currentPnL = calculatePnL();
        
        // If profit exceeds a certain threshold, take profit and reduce positions
        if (currentPnL > 300) {
            System.out.println("Profit threshold reached. Taking profits and reducing positions.");
            reducePosition();
        } else if (currentPnL < -200) {
            // If losses exceed a certain threshold, stop trading to avoid further losses
            System.out.println("Loss threshold reached. Halting trading.");
            stop();
        }
    }

    // Method to reduce positions
    private void reducePosition() {
        double reductionAmount = randomGenerator.nextDouble() * 2; 
        inventoryPosition -= reductionAmount;

        // Ensure the position is within bounds
        if (inventoryPosition < -maxInventory) {
            inventoryPosition = -maxInventory;
        }

        System.out.println("Position reduced by: " + reductionAmount + ". Current inventory: " + inventoryPosition);
    }

    // Method to order fill based on market conditions
    private void simulateOrderFill(String side, double price) {
        double fillProbability = randomGenerator.nextDouble(); 

        if (fillProbability > 0.5) {
            // Order fill and inventory adjustment
            if (side.equals("BUY")) {
                inventoryPosition += randomGenerator.nextDouble();
            } else if (side.equals("SELL")) {
                inventoryPosition -= randomGenerator.nextDouble();
            }
            
            // Log the order fill
            System.out.println("Order " + side + " at price: " + price + " was filled.");
        } else {
            System.out.println("Order " + side + " at price: " + price + " was not filled.");
        }
    }

    // Method to simulate random external market events (news)
    private void simulateExternalEvent() {
        double eventProbability = randomGenerator.nextDouble(); 

        if (eventProbability > 0.9) {
            // High impact event, increase volatility
            volatility += 0.2;
            System.out.println("High impact market event occurred! Volatility increased to: " + volatility);
        } else if (eventProbability > 0.7) {
            // Low impact event, slightly increase volatility
            volatility += 0.1;
            System.out.println("Market event occurred. Volatility slightly increased to: " + volatility);
        } else {
            System.out.println("No significant market event detected.");
        }
    }

    // Method to execute the main market making loop
    public void runMarketMaking() {
        start();
        
        while (running.get()) {
            simulateExternalEvent();  
            managePnL(); 
            adjustInventoryBasedOnRisk(); 
            adjustTradingFrequency(); 
        }
    }
}
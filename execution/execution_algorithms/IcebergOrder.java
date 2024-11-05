package execution.execution_algorithms;

import java.util.Random;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.Timer;
import java.util.TimerTask;

public class IcebergOrder {
    private static final Logger logger = Logger.getLogger(IcebergOrder.class.getName());

    private double totalOrderSize;
    private double visibleOrderSize;
    private double hiddenOrderSize;
    private double executedSize;
    private double remainingSize;
    private String symbol;
    private String side;  // Buy or Sell
    private double price;
    private BrokerConnector broker;
    private boolean paused;
    private boolean stopLossTriggered;
    private double stopLossThreshold;
    private double takeProfitThreshold;
    private double marketPrice;

    public IcebergOrder(String symbol, double totalOrderSize, double visibleOrderSize, String side, double price,
                        double stopLossThreshold, double takeProfitThreshold, BrokerConnector broker) {
        this.symbol = symbol;
        this.totalOrderSize = totalOrderSize;
        this.visibleOrderSize = visibleOrderSize;
        this.hiddenOrderSize = totalOrderSize - visibleOrderSize;
        this.side = side;
        this.price = price;
        this.broker = broker;
        this.executedSize = 0;
        this.remainingSize = totalOrderSize;
        this.paused = false;
        this.stopLossTriggered = false;
        this.stopLossThreshold = stopLossThreshold;
        this.takeProfitThreshold = takeProfitThreshold;
        this.marketPrice = broker.getMarketPrice(symbol);

        logger.setLevel(Level.INFO);
    }

    public void executeOrder() {
        while (remainingSize > 0 && !stopLossTriggered) {
            if (paused) {
                logger.info("Execution is paused. Waiting...");
                try {
                    Thread.sleep(1000); // Prevent busy-waiting
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    logger.severe("Execution interrupted while paused: " + e.getMessage());
                }
                continue;
            }

            updateMarketPrice();

            if (isStopLossTriggered()) {
                handleStopLoss();
                break;
            }

            if (isTakeProfitReached()) {
                handleTakeProfit();
                break;
            }

            double sizeToExecute = Math.min(visibleOrderSize, remainingSize);
            sendOrder(sizeToExecute);
            remainingSize -= sizeToExecute;
            updateHiddenOrderSize();
            pauseExecution();
        }

        if (stopLossTriggered) {
            logger.warning("Stop loss triggered. Terminating execution.");
        } else if (remainingSize <= 0) {
            logger.info("Execution completed successfully.");
        }
    }

    private void updateMarketPrice() {
        this.marketPrice = broker.getMarketPrice(symbol);
    }

    private boolean isStopLossTriggered() {
        if (side.equalsIgnoreCase("buy") && marketPrice <= stopLossThreshold) {
            logger.warning("Stop loss triggered at price " + marketPrice);
            stopLossTriggered = true;
            return true;
        } else if (side.equalsIgnoreCase("sell") && marketPrice >= stopLossThreshold) {
            logger.warning("Stop loss triggered at price " + marketPrice);
            stopLossTriggered = true;
            return true;
        }
        return false;
    }

    private boolean isTakeProfitReached() {
        if (side.equalsIgnoreCase("buy") && marketPrice >= takeProfitThreshold) {
            logger.info("Take profit reached at price " + marketPrice);
            return true;
        } else if (side.equalsIgnoreCase("sell") && marketPrice <= takeProfitThreshold) {
            logger.info("Take profit reached at price " + marketPrice);
            return true;
        }
        return false;
    }

    private void handleStopLoss() {
        logger.severe("Executing stop loss order for " + symbol);
        double sizeToClose = remainingSize;
        if (side.equalsIgnoreCase("buy")) {
            broker.sendSellOrder(symbol, sizeToClose, marketPrice);
        } else if (side.equalsIgnoreCase("sell")) {
            broker.sendBuyOrder(symbol, sizeToClose, marketPrice);
        }
        executedSize += sizeToClose;
        remainingSize = 0;
        logProgress();
    }

    private void handleTakeProfit() {
        logger.info("Executing take profit for " + symbol);
        double sizeToClose = remainingSize;
        if (side.equalsIgnoreCase("buy")) {
            broker.sendSellOrder(symbol, sizeToClose, marketPrice);
        } else if (side.equalsIgnoreCase("sell")) {
            broker.sendBuyOrder(symbol, sizeToClose, marketPrice);
        }
        executedSize += sizeToClose;
        remainingSize = 0;
        logProgress();
    }

    private void sendOrder(double sizeToExecute) {
        if (side.equalsIgnoreCase("buy")) {
            broker.sendBuyOrder(symbol, sizeToExecute, price);
        } else if (side.equalsIgnoreCase("sell")) {
            broker.sendSellOrder(symbol, sizeToExecute, price);
        }
        executedSize += sizeToExecute;
        logger.info("Executed " + sizeToExecute + " units of " + symbol + " at price " + price);
        logProgress();
    }

    private void updateHiddenOrderSize() {
        hiddenOrderSize = Math.max(0, remainingSize - visibleOrderSize);
        logger.info("Remaining hidden order size: " + hiddenOrderSize);
    }

    private void pauseExecution() {
        try {
            Random random = new Random();
            int delay = random.nextInt(5000) + 1000;  // Delay between 1 and 5 seconds
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            logger.severe("Execution interrupted: " + e.getMessage());
        }
    }

    private void logProgress() {
        double progress = (executedSize / totalOrderSize) * 100;
        logger.info(String.format("Order execution progress: %.2f%%", progress));
    }

    public void pauseOrder() {
        paused = true;
        logger.info("Order execution paused.");
    }

    public void resumeOrder() {
        paused = false;
        logger.info("Order execution resumed.");
    }

    public void cancelOrder() {
        remainingSize = 0;
        logger.info("Order cancelled. Remaining size set to 0.");
    }

    public static void main(String[] args) {
        BrokerConnector broker = new BrokerConnector();
        IcebergOrder icebergOrder = new IcebergOrder("AAPL", 1000, 100, "buy", 150.00, 145.00, 160.00, broker);
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                icebergOrder.executeOrder();
            }
        }, 0);
    }
}

class BrokerConnector {
    public double getMarketPrice(String symbol) {
        // Simulate retrieving the current market price from an exchange
        return 150.00 + (new Random().nextDouble() - 0.5) * 10;  // Fluctuate around 150.00
    }

    public void sendBuyOrder(String symbol, double size, double price) {
        // Logic to send a buy order to the exchange
        System.out.println("Sending buy order: " + size + " units of " + symbol + " at " + price);
    }

    public void sendSellOrder(String symbol, double size, double price) {
        // Logic to send a sell order to the exchange
        System.out.println("Sending sell order: " + size + " units of " + symbol + " at " + price);
    }
}
package risk_management;

import java.util.HashMap;
import java.util.Map;
import java.util.Date;
import java.text.SimpleDateFormat;
import java.util.logging.Logger;
import java.util.logging.FileHandler;
import java.util.logging.SimpleFormatter;

public class compliance {
    private Map<String, Double> riskLimits;
    private Map<String, Double> positions;
    private Map<String, Double> tradeVolumes;
    private double maxLossLimit;
    private double currentLoss;
    private Logger logger;
    private SimpleDateFormat dateFormat;

    public compliance(double maxLossLimit) {
        this.maxLossLimit = maxLossLimit;
        this.currentLoss = 0.0;
        this.riskLimits = new HashMap<>();
        this.positions = new HashMap<>();
        this.tradeVolumes = new HashMap<>();
        this.dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        initializeLogger();
    }

    // Initialize the logger for recording compliance activity
    private void initializeLogger() {
        try {
            logger = Logger.getLogger("ComplianceLog");
            FileHandler fileHandler = new FileHandler("compliance_log.log", true);
            SimpleFormatter formatter = new SimpleFormatter();
            fileHandler.setFormatter(formatter);
            logger.addHandler(fileHandler);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Set a position limit for a specific asset
    public void setRiskLimit(String asset, double limit) {
        riskLimits.put(asset, limit);
        logEvent("Risk limit set for asset: " + asset + " to " + limit);
    }

    // Check if the current position exceeds the set limit
    public boolean checkPosition(String asset, double position) {
        if (!riskLimits.containsKey(asset)) {
            throw new IllegalArgumentException("No limit set for asset: " + asset);
        }
        return position <= riskLimits.get(asset);
    }

    // Update position for an asset and log the activity
    public void updatePosition(String asset, double newPosition) {
        if (!checkPosition(asset, newPosition)) {
            throw new IllegalArgumentException("Position limit exceeded for asset: " + asset);
        }
        positions.put(asset, newPosition);
        logEvent("Updated position for asset: " + asset + " to " + newPosition);
    }

    // Method to track trade volume per asset
    public void updateTradeVolume(String asset, double volume) {
        double totalVolume = tradeVolumes.getOrDefault(asset, 0.0) + volume;
        tradeVolumes.put(asset, totalVolume);
        logEvent("Updated trade volume for asset: " + asset + " to " + totalVolume);
    }

    // Method to register a trade loss
    public void registerLoss(double loss) {
        currentLoss += loss;
        logEvent("Registered loss of " + loss + ". Current total loss: " + currentLoss);
        if (currentLoss > maxLossLimit) {
            triggerLossLimitViolation();
        }
    }

    // Method to check if the loss limit is violated
    private void triggerLossLimitViolation() {
        logEvent("Warning: Maximum loss limit exceeded!");
        System.out.println("Warning: Maximum loss limit exceeded!");
        // Logic to halt further trading, notify relevant parties, etc.
    }

    // Method to register a violation
    private void registerViolation(String message) {
        logEvent("Compliance violation: " + message);
        System.out.println("Compliance violation: " + message);
        // Halt trading or other necessary action
    }

    // Check if all trading activities comply with regulations
    public boolean checkCompliance() {
        boolean compliant = true;
        
        for (Map.Entry<String, Double> entry : positions.entrySet()) {
            if (!checkPosition(entry.getKey(), entry.getValue())) {
                registerViolation("Position limit exceeded for asset: " + entry.getKey());
                compliant = false;
            }
        }

        if (currentLoss > maxLossLimit) {
            registerViolation("Loss limit exceeded.");
            compliant = false;
        }

        return compliant;
    }

    // Additional compliance check for volume-based trading restrictions
    public boolean checkVolumeCompliance(String asset, double volumeLimit) {
        double totalVolume = tradeVolumes.getOrDefault(asset, 0.0);
        if (totalVolume > volumeLimit) {
            registerViolation("Trade volume limit exceeded for asset: " + asset);
            return false;
        }
        return true;
    }

    // Generate compliance report
    public String generateReport() {
        StringBuilder report = new StringBuilder();
        report.append("Compliance Report: ").append(getCurrentTime()).append("\n");
        report.append("Current Loss: ").append(currentLoss).append("\n");
        report.append("Max Loss Limit: ").append(maxLossLimit).append("\n");

        for (Map.Entry<String, Double> entry : positions.entrySet()) {
            report.append("Asset: ").append(entry.getKey())
                  .append(", Position: ").append(entry.getValue())
                  .append(", Limit: ").append(riskLimits.get(entry.getKey())).append("\n");
        }

        for (Map.Entry<String, Double> entry : tradeVolumes.entrySet()) {
            report.append("Asset: ").append(entry.getKey())
                  .append(", Trade Volume: ").append(entry.getValue()).append("\n");
        }

        return report.toString();
    }

    // Get current time in formatted string
    private String getCurrentTime() {
        return dateFormat.format(new Date());
    }

    // Log events related to compliance activities
    private void logEvent(String event) {
        String timestampedEvent = getCurrentTime() + " - " + event;
        logger.info(timestampedEvent);
        System.out.println(timestampedEvent);  // Print to console
    }

    public static void main(String[] args) {
        compliance compliance = new compliance(50000);  // Max loss limit set to 50,000
        compliance.setRiskLimit("AAPL", 1000);  // Limit set for Apple stock
        compliance.setRiskLimit("GOOGL", 500);  // Limit set for Google stock
        compliance.setRiskLimit("TSLA", 800);   // Limit set for Tesla stock

        // Simulate trade activities
        try {
            compliance.updatePosition("AAPL", 900);  // Within limit
            compliance.registerLoss(20000);  // Registering a loss
            compliance.updateTradeVolume("AAPL", 300);  // Update trade volume
            compliance.updatePosition("GOOGL", 450);  // Within limit
            compliance.updatePosition("TSLA", 850);  // Exceeds limit
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }

        // Additional compliance checks
        boolean volumeCompliance = compliance.checkVolumeCompliance("AAPL", 500);
        System.out.println("Volume compliance for AAPL: " + volumeCompliance);

        // Generate compliance report
        String report = compliance.generateReport();
        System.out.println(report);
    }
}
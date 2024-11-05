package analytics;

import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

public class AnomalyDetection {

    private double threshold;
    private List<Double> dataWindow;
    private int windowSize;
    private double lowerBound, upperBound;
    private static final Logger logger = Logger.getLogger(AnomalyDetection.class.getName());

    // Enum for types of anomalies
    public enum AnomalyType {
        SPIKE, DROPOUT, VOLATILITY
    }

    public AnomalyDetection(double threshold, int windowSize) {
        this.threshold = threshold;
        this.windowSize = windowSize;
        this.dataWindow = new ArrayList<>();
        this.lowerBound = 0.0;
        this.upperBound = 0.0;
    }

    // Add data to the window and detect anomalies
    public void addData(double newData) {
        if (dataWindow.size() >= windowSize) {
            dataWindow.remove(0);
        }
        dataWindow.add(newData);

        if (dataWindow.size() == windowSize) {
            double mean = calculateMean();
            double stdDev = calculateStandardDeviation(mean);
            lowerBound = mean - threshold * stdDev;
            upperBound = mean + threshold * stdDev;

            detectAnomalies(newData, mean, stdDev);
        }
    }

    // Calculate the mean of the data in the window
    private double calculateMean() {
        double sum = 0.0;
        for (double value : dataWindow) {
            sum += value;
        }
        return sum / dataWindow.size();
    }

    // Calculate the standard deviation of the data in the window
    private double calculateStandardDeviation(double mean) {
        double sum = 0.0;
        for (double value : dataWindow) {
            sum += Math.pow(value - mean, 2);
        }
        return Math.sqrt(sum / dataWindow.size());
    }

    // Detect anomalies based on various conditions
    private void detectAnomalies(double data, double mean, double stdDev) {
        // Spike Detection
        if (isAnomaly(data, mean, stdDev, AnomalyType.SPIKE)) {
            logAnomaly(AnomalyType.SPIKE, data);
        }

        // Dropout Detection (sharp drop)
        if (isAnomaly(data, mean, stdDev, AnomalyType.DROPOUT)) {
            logAnomaly(AnomalyType.DROPOUT, data);
        }

        // Volatility Detection
        if (isAnomaly(data, mean, stdDev, AnomalyType.VOLATILITY)) {
            logAnomaly(AnomalyType.VOLATILITY, data);
        }
    }

    // Check if the new data point is an anomaly based on the threshold and type of anomaly
    private boolean isAnomaly(double data, double mean, double stdDev, AnomalyType type) {
        switch (type) {
            case SPIKE:
                return data > upperBound;
            case DROPOUT:
                return data < lowerBound;
            case VOLATILITY:
                // Detect unusual increase in volatility
                double previousData = dataWindow.get(dataWindow.size() - 2);
                return Math.abs(data - previousData) > threshold * stdDev;
            default:
                return false;
        }
    }

    // Log detected anomaly information
    private void logAnomaly(AnomalyType type, double data) {
        switch (type) {
            case SPIKE:
                logger.info("Spike detected: " + data + " exceeds upper bound of " + upperBound);
                break;
            case DROPOUT:
                logger.warning("Dropout detected: " + data + " falls below lower bound of " + lowerBound);
                break;
            case VOLATILITY:
                logger.info("High volatility detected with data: " + data);
                break;
        }
    }

    // Get the anomaly type description
    public String getAnomalyDescription(AnomalyType type) {
        switch (type) {
            case SPIKE:
                return "Spike: Anomalous rise in market data.";
            case DROPOUT:
                return "Dropout: Anomalous drop in market data.";
            case VOLATILITY:
                return "Volatility: Sudden fluctuation in market data.";
            default:
                return "Unknown anomaly type.";
        }
    }

    // Get the current upper bound based on the last calculated mean and standard deviation
    public double getUpperBound() {
        return upperBound;
    }

    // Get the current lower bound based on the last calculated mean and standard deviation
    public double getLowerBound() {
        return lowerBound;
    }

    // Get the window size for anomaly detection
    public int getWindowSize() {
        return windowSize;
    }

    // Set a new window size for detecting anomalies
    public void setWindowSize(int windowSize) {
        if (windowSize > 0) {
            this.windowSize = windowSize;
            logger.info("Window size updated to " + windowSize);
        } else {
            logger.warning("Window size must be greater than 0.");
        }
    }

    // Set a new threshold for detecting anomalies
    public void setThreshold(double threshold) {
        if (threshold > 0) {
            this.threshold = threshold;
            logger.info("Threshold updated to " + threshold);
        } else {
            logger.warning("Threshold must be greater than 0.");
        }
    }

    // Get the current threshold
    public double getThreshold() {
        return threshold;
    }

    // Clear the current data window
    public void clearDataWindow() {
        dataWindow.clear();
        logger.info("Data window cleared.");
    }

    public static void main(String[] args) {
        // Usage with a threshold of 2 standard deviations and a window size of 10
        AnomalyDetection anomalyDetector = new AnomalyDetection(2.0, 10);

        // Simulating streaming market data
        double[] marketData = {100.0, 102.0, 101.5, 99.0, 105.0, 98.0, 101.0, 110.0, 112.0, 115.0, 130.0, 90.0, 85.0, 140.0};

        for (double data : marketData) {
            anomalyDetector.addData(data);
        }

        // Accessing anomaly descriptions
        System.out.println(anomalyDetector.getAnomalyDescription(AnomalyType.SPIKE));
        System.out.println(anomalyDetector.getAnomalyDescription(AnomalyType.DROPOUT));
        System.out.println(anomalyDetector.getAnomalyDescription(AnomalyType.VOLATILITY));

        // Accessing current upper and lower bounds
        System.out.println("Current Upper Bound: " + anomalyDetector.getUpperBound());
        System.out.println("Current Lower Bound: " + anomalyDetector.getLowerBound());

        // Clearing data window and resetting window size
        anomalyDetector.clearDataWindow();
        anomalyDetector.setWindowSize(20);
        anomalyDetector.setThreshold(3.0);
    }
}
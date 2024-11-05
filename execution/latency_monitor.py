import time
import statistics
import logging
from collections import deque
from datetime import datetime

logging.basicConfig(filename="latency_monitor.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class LatencyMonitor:
    def __init__(self, threshold_ms=5.0, window_size=100):
        self.latencies = deque(maxlen=window_size)
        self.threshold_ms = threshold_ms
        self.window_size = window_size
        self.high_latency_count = 0
        self.total_executions = 0
        self.start_time = datetime.now()
        self.alert_triggered = False

    def record_latency(self, start_time, end_time):
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        self.latencies.append(latency)
        self.total_executions += 1
        
        # Log latency data for real-time monitoring
        logging.info(f"Latency recorded: {latency:.4f} ms")

    def average_latency(self):
        if self.latencies:
            return statistics.mean(self.latencies)
        return 0.0

    def latency_std_dev(self):
        if len(self.latencies) > 1:
            return statistics.stdev(self.latencies)
        return 0.0

    def latency_percentile(self, percentile):
        if self.latencies:
            sorted_latencies = sorted(self.latencies)
            index = int(len(sorted_latencies) * (percentile / 100))
            return sorted_latencies[index]
        return 0.0

    def check_threshold(self):
        avg_latency = self.average_latency()
        if avg_latency > self.threshold_ms:
            self.high_latency_count += 1
            logging.warning(f"Latency threshold exceeded: {avg_latency:.4f} ms")
            return False
        return True

    def dynamic_threshold_adjustment(self):
        avg_latency = self.average_latency()
        stddev_latency = self.latency_std_dev()
        
        # Dynamically adjust threshold based on historical performance
        if stddev_latency > 0:
            new_threshold = avg_latency + 2 * stddev_latency
            if new_threshold > self.threshold_ms:
                logging.info(f"Adjusting latency threshold from {self.threshold_ms:.4f} ms to {new_threshold:.4f} ms")
                self.threshold_ms = new_threshold

    def monitor_execution(self, execution_fn, *args, **kwargs):
        start_time = time.perf_counter()
        
        # Execute the provided function (order execution, API call, etc)
        result = execution_fn(*args, **kwargs)
        
        end_time = time.perf_counter()
        
        # Record the latency
        self.record_latency(start_time, end_time)
        
        # Check if latency exceeds the threshold
        if not self.check_threshold():
            # Trigger latency optimization logic (alert or adjustment)
            self.optimize_performance()
        
        # Dynamic threshold adjustment based on performance
        self.dynamic_threshold_adjustment()
        
        return result

    def optimize_performance(self):
        # Optimization logic for reducing latency
        if not self.alert_triggered:
            self.trigger_alert()
            logging.warning("Performance optimization triggered due to high latency.")
            
            # Rerouting orders to less busy servers
            if self.server_load > self.threshold:
                self.reroute_orders()
                logging.info("Orders rerouted to reduce load on current server.")
            
            # Adjusting API calls, reducing batch sizes or throttling requests
            if self.api_call_rate > self.max_api_rate:
                self.adjust_api_calls()
                logging.info("API call rate adjusted to reduce latency.")
            
            # Scaling resources (spin up additional instances)
            if self.resource_utilization > self.utilization_threshold:
                self.scale_resources()
                logging.info("Resources scaled up to manage increased demand.")

    def trigger_alert(self):
        # Trigger an alert
        self.alert_triggered = True
        logging.error(f"ALERT: High latency detected. Average latency: {self.average_latency():.4f} ms")
        import smtplib
        recipient = "admin@website.com"
        sender = "monitor@website.com"
        message = f"Subject: High Latency Alert\n\nHigh latency detected. Average latency: {self.average_latency():.4f} ms"
    
        with smtplib.SMTP('smtp.website.com') as server:
            server.sendmail(sender, recipient, message)
        
    def reset_alert(self):
        self.alert_triggered = False
        logging.info("Latency alert reset.")

    def report_statistics(self):
        # Generate detailed latency statistics
        avg_latency = self.average_latency()
        stddev_latency = self.latency_std_dev()
        p95_latency = self.latency_percentile(95)
        p99_latency = self.latency_percentile(99)

        logging.info(f"Latency Statistics: Average: {avg_latency:.4f} ms, "
                     f"Std Dev: {stddev_latency:.4f} ms, 95th Percentile: {p95_latency:.4f} ms, "
                     f"99th Percentile: {p99_latency:.4f} ms")

    def session_summary(self):
        # Summary of the current monitoring session
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        avg_latency = self.average_latency()
        high_latency_pct = (self.high_latency_count / self.total_executions) * 100 if self.total_executions > 0 else 0

        summary = (f"Monitoring Session Summary:\n"
                   f"Total Executions: {self.total_executions}\n"
                   f"Elapsed Time: {elapsed_time:.2f} seconds\n"
                   f"Average Latency: {avg_latency:.4f} ms\n"
                   f"High Latency Count: {self.high_latency_count} ({high_latency_pct:.2f}%)")

        logging.info(summary)
        print(summary)

    def run_continuous_monitor(self, execution_fn, *args, iterations=1000, **kwargs):
        # Continuous monitoring loop with specified iterations
        for _ in range(iterations):
            self.monitor_execution(execution_fn, *args, **kwargs)
            time.sleep(0.001)  # Simulate some delay between executions
        
        self.session_summary()

# Function for testing latency monitoring
def mock_order_execution():
    time.sleep(0.003)  # Simulate some execution delay (sending an order to the exchange)
    return "Order executed"

# Advanced test function to simulate variable latency
def mock_order_execution_with_latency(latency_ms):
    time.sleep(latency_ms / 1000.0)  # Simulate variable delay
    return f"Order executed in {latency_ms:.2f} ms"

if __name__ == "__main__":
    latency_monitor = LatencyMonitor(threshold_ms=5.0, window_size=50)
    
    # Simulate multiple executions to monitor latency over time
    for i in range(100):
        # Simulate variable latency between 1ms and 10ms
        latency = i % 10 + 1
        latency_monitor.monitor_execution(mock_order_execution_with_latency, latency)
    
    # Report final statistics
    latency_monitor.report_statistics()
    latency_monitor.session_summary()

    # Continuous monitoring session 
    latency_monitor.run_continuous_monitor(mock_order_execution_with_latency, latency_ms=3, iterations=200)
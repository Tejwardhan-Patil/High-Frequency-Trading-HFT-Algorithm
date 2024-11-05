import os
import csv
import json
import pandas as pd
from datetime import datetime
from risk_management.limits import check_risk_limits
from risk_management.real_time_monitoring import get_real_time_metrics
from analytics.performance_metrics import calculate_performance_metrics
import logging
import matplotlib.pyplot as plt

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Directory paths
REPORTS_DIR = "reports/"
DATA_DIR = "data/processed/aggregated_data/"
RISK_LIMITS_PATH = "configs/risk_limits.json"

# Ensure the report directory exists
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# Constants for report types
REPORT_TYPE_CSV = "csv"
REPORT_TYPE_JSON = "json"
REPORT_TYPE_BOTH = "both"

def generate_csv_report(report_data, filename):
    """Generates a CSV report with the given data."""
    csv_file = os.path.join(REPORTS_DIR, filename)
    try:
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(report_data.keys())
            writer.writerows(zip(*report_data.values()))
        logger.info(f"CSV report generated at {csv_file}")
    except Exception as e:
        logger.error(f"Error generating CSV report: {e}")
    return csv_file

def generate_json_report(report_data, filename):
    """Generates a JSON report with the given data."""
    json_file = os.path.join(REPORTS_DIR, filename)
    try:
        with open(json_file, 'w') as file:
            json.dump(report_data, file, indent=4)
        logger.info(f"JSON report generated at {json_file}")
    except Exception as e:
        logger.error(f"Error generating JSON report: {e}")
    return json_file

def compile_risk_metrics():
    """Compile risk metrics from real-time monitoring and risk limits."""
    real_time_metrics = get_real_time_metrics()
    logger.info("Real-time metrics fetched successfully.")
    try:
        with open(RISK_LIMITS_PATH, 'r') as file:
            risk_limits = json.load(file)
        logger.info("Risk limits loaded from configuration.")
    except FileNotFoundError:
        logger.error("Risk limits configuration file not found.")
        risk_limits = {}
    
    risk_status = check_risk_limits(real_time_metrics, risk_limits)
    return {
        "real_time_metrics": real_time_metrics,
        "risk_limits": risk_limits,
        "risk_status": risk_status
    }

def compile_performance_metrics():
    """Compile performance metrics from aggregated trading data."""
    aggregated_data_path = os.path.join(DATA_DIR, "trading_data.csv")
    try:
        aggregated_data = pd.read_csv(aggregated_data_path)
        logger.info("Aggregated trading data loaded.")
    except FileNotFoundError:
        logger.error(f"Aggregated data file not found at {aggregated_data_path}")
        return {}

    performance_metrics = calculate_performance_metrics(aggregated_data)
    return performance_metrics

def visualize_performance(performance_metrics, filename):
    """Visualizes key performance metrics and saves the plot."""
    try:
        fig, ax = plt.subplots()
        ax.plot(performance_metrics['Date'], performance_metrics['Returns'], label='Returns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Returns')
        ax.set_title('Performance Over Time')
        ax.legend()

        # Save plot
        plot_file = os.path.join(REPORTS_DIR, filename)
        plt.savefig(plot_file)
        logger.info(f"Performance plot saved at {plot_file}")
    except Exception as e:
        logger.error(f"Error creating performance visualization: {e}")

def generate_combined_report(report_data, filename):
    """Generates both CSV and JSON reports."""
    csv_file = generate_csv_report(report_data, f"{filename}.csv")
    json_file = generate_json_report(report_data, f"{filename}.json")
    return csv_file, json_file

def generate_report(report_type=REPORT_TYPE_CSV, include_visuals=False):
    """Generates a report for compliance and risk management."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}"

    # Compile report data
    risk_metrics = compile_risk_metrics()
    performance_metrics = compile_performance_metrics()

    if not risk_metrics or not performance_metrics:
        logger.error("Could not generate report due to missing data.")
        return None

    report_data = {
        "Risk_Metrics": risk_metrics,
        "Performance_Metrics": performance_metrics
    }

    # Generate reports in specified format
    if report_type == REPORT_TYPE_CSV:
        report_file = generate_csv_report(report_data, f"{filename}.csv")
    elif report_type == REPORT_TYPE_JSON:
        report_file = generate_json_report(report_data, f"{filename}.json")
    elif report_type == REPORT_TYPE_BOTH:
        report_file = generate_combined_report(report_data, filename)
    else:
        raise ValueError("Unsupported report type")

    # Generate visualizations
    if include_visuals and report_type != REPORT_TYPE_JSON:
        visualize_performance(performance_metrics, f"{filename}_plot.png")

    return report_file

def summary_risk_status(risk_status):
    """Generates a brief summary of risk status."""
    summary = ""
    if risk_status['breached']:
        summary = "Risk limits breached. Immediate action required."
    else:
        summary = "No risk limit breaches detected."
    logger.info(summary)
    return summary

def save_summary_report(summary, filename):
    """Save summary report as a text file."""
    try:
        summary_file = os.path.join(REPORTS_DIR, filename)
        with open(summary_file, 'w') as file:
            file.write(summary)
        logger.info(f"Summary report saved at {summary_file}")
    except Exception as e:
        logger.error(f"Error saving summary report: {e}")

def enhanced_report_generation():
    """Extended report generation with additional options."""
    report_type = input("Enter report type (csv, json, both): ")
    include_visuals = input("Include visualizations? (yes/no): ").lower() == 'yes'

    try:
        report_file = generate_report(report_type, include_visuals)
        if report_file:
            logger.info(f"Report generated successfully: {report_file}")
        else:
            logger.error("Report generation failed.")
    except Exception as e:
        logger.error(f"Error during report generation: {e}")

def archive_old_reports(days_old=30):
    """Archives reports older than a specified number of days."""
    now = datetime.now()
    for filename in os.listdir(REPORTS_DIR):
        filepath = os.path.join(REPORTS_DIR, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - file_time).days > days_old:
                try:
                    os.remove(filepath)
                    logger.info(f"Archived old report: {filename}")
                except Exception as e:
                    logger.error(f"Error archiving report: {e}")

if __name__ == "__main__":
    logger.info("Starting report generation process.")
    enhanced_report_generation()
    archive_old_reports(30)
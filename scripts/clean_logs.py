import os
import time
from pathlib import Path

# Define the directory where logs are stored
LOG_DIR = Path("/var/logs/hft_logs")

# Define the age limit (in days) for log retention
LOG_RETENTION_DAYS = 30

# Get the current time in seconds since epoch
current_time = time.time()

# Convert retention days to seconds
retention_period = LOG_RETENTION_DAYS * 86400

# Function to delete old logs
def clean_old_logs(log_dir: Path, retention_period: int):
    if log_dir.exists() and log_dir.is_dir():
        for log_file in log_dir.iterdir():
            if log_file.is_file():
                file_age = current_time - log_file.stat().st_mtime
                if file_age > retention_period:
                    try:
                        log_file.unlink()  # Delete the file
                        print(f"Deleted old log file: {log_file}")
                    except Exception as e:
                        print(f"Error deleting file {log_file}: {e}")
    else:
        print(f"Log directory {log_dir} does not exist or is not accessible")

if __name__ == "__main__":
    clean_old_logs(LOG_DIR, retention_period)
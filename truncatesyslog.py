import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Log file path
cef_file_path = "/var/log/anomalyhunter/anomaly.syslog"

def read_existing_logs():
    """Read existing logs from the CEF log file and filter entries within the last 24 hours."""
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    existing_logs = []
    if os.path.exists(cef_file_path):
        with open(cef_file_path, "r") as cef_file:
            for line in cef_file:
                if line.startswith("CEF:"):
                    # Extract timestamp from the CEF event
                    parts = line.split(" rt=")
                    if len(parts) > 1:
                        timestamp_str = parts[1].split()[0]
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            if timestamp >= twenty_four_hours_ago:
                                existing_logs.append(line.strip())
                        except ValueError:
                            logger.error(f"Error parsing timestamp: {timestamp_str}")
    return existing_logs

def write_to_cef(existing_logs):
    """Write the filtered logs to the CEF log file."""
    with open(cef_file_path, "w") as cef_file:
        for log in existing_logs:
            cef_file.write(log + "\n")
        logging.info(f"Truncated log file to keep only the last 24 hours of logs")

def truncate_logs():
    """Truncate the log file to keep only the last 24 hours of logs."""
    existing_logs = read_existing_logs()
    write_to_cef(existing_logs)

if __name__ == "__main__":
    truncate_logs()

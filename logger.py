import os
import logging
import schedule
import time  # Import the time module
import mysql.connector
from datetime import datetime
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Log file paths
cef_file_path = "/var/log/anomalyhunter/anomaly.syslog"
log_dir = "/var/log/anomalyhunter"

# Database configuration
db_config = {
    "host": "localhost",
    "user": "sigma",
    "password": "sigma",
    "database": "sigma_db",
    "pool_name": "mypool",
    "pool_size": 5
}

# Create a connection pool
connection_pool = MySQLConnectionPool(**db_config)

# Helper functions
def fetch_anomalies():
    """Fetch anomalies (cluster -1) from the sigma_alerts table."""
    try:
        connection = connection_pool.get_connection()
        with connection.cursor() as cursor:
            select_query = """
            SELECT id, title, tags, description, system_time, computer_name, user_id, event_id, provider_name, dbscan_cluster, raw
            FROM sigma_alerts
            WHERE dbscan_cluster = -1
            """
            cursor.execute(select_query)
            anomalies = cursor.fetchall()
        return anomalies
    except Error as e:
        logging.error(f"Error fetching anomalies: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def ensure_directory_exists(directory):
    """Ensure the directory exists and has write permissions."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, 0o777)

def load_logged_anomalies():
    """Load anomalies from the CEF log file."""
    if not os.path.exists(cef_file_path):
        return set()

    logged_anomalies = set()
    with open(cef_file_path, "r") as cef_file:
        for line in cef_file:
            if line.startswith("CEF:"):
                logged_anomalies.add(line.strip())
    return logged_anomalies

def write_to_cef(anomalies, logged_anomalies):
    """Write anomalies to the CEF log file."""
    new_logs = []
    with open(cef_file_path, "a") as cef_file:
        for anomaly in anomalies:
            # Format the anomaly into a CEF event
            cef_event = (
                f"CEF:0|Sigma|UEBA|1.0|{anomaly[7]}|{anomaly[1]}|5|"
                f"end={anomaly[4]} rt={anomaly[4]} suser={anomaly[6]} dvc={anomaly[5]} "
                f"msg={anomaly[3]} cs1={anomaly[8]} cs1Label=ProviderName "
                f"cs2={anomaly[2]} cs2Label=Tags cs3={anomaly[9]} cs3Label=DBScanCluster "
                f"cs4={anomaly[10]} cs4Label=Raw"
            )
            if cef_event not in logged_anomalies:
                cef_file.write(cef_event + "\n")
                new_logs.append(cef_event)
                logging.info(f"Logged anomaly: {cef_event}")

def detect_and_log_anomalies():
    """Detect anomalies and log them."""
    ensure_directory_exists(log_dir)
    logged_anomalies = load_logged_anomalies()
    anomalies = fetch_anomalies()
    write_to_cef(anomalies, logged_anomalies)

# Run the script immediately with existing data
detect_and_log_anomalies()

# Schedule anomaly detection and logging every 1 minute
schedule.every(1).minute.do(detect_and_log_anomalies)

while True:
    schedule.run_pending()
    time.sleep(1)

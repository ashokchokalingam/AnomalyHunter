import mysql.connector
from mysql.connector import Error
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Database configuration
db_config = {
    "host": "localhost",
    "user": "sigma",
    "password": "sigma",
    "database": "sigma_db",
}

# Initialize SQL tables
def initialize_sql_tables():
    """Create the sigma_alerts and dbscan_outlier tables in the database if they don't exist."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Create sigma_alerts table
                create_sigma_alerts_query = """
                CREATE TABLE IF NOT EXISTS sigma_alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    tags TEXT,
                    description TEXT,
                    system_time DATETIME,
                    computer_name VARCHAR(100),
                    user_id VARCHAR(100),
                    event_id VARCHAR(50),
                    provider_name VARCHAR(100),
                    dbscan_cluster INT,
                    raw TEXT,
                    rule_id VARCHAR(50),
                    rule_level VARCHAR(50),
                    task VARCHAR(255)
                );
                """
                cursor.execute(create_sigma_alerts_query)

                # Create dbscan_outlier table
                create_dbscan_outlier_query = """
                CREATE TABLE IF NOT EXISTS dbscan_outlier (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    tags TEXT,
                    description TEXT,
                    system_time DATETIME,
                    computer_name VARCHAR(100),
                    user_id VARCHAR(100),
                    event_id VARCHAR(50),
                    provider_name VARCHAR(100),
                    dbscan_cluster INT,
                    raw TEXT,
                    rule_id VARCHAR(50),
                    rule_level VARCHAR(50),
                    task VARCHAR(255)
                );
                """
                cursor.execute(create_dbscan_outlier_query)

                connection.commit()
                logger.info("Initialized SQL tables 'sigma_alerts' and 'dbscan_outlier'.")
    except Error as e:
        logger.error(f"Error initializing SQL tables: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

def insert_alert(alert_data):
    """Insert alert data into the sigma_alerts table."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO sigma_alerts (
                    title, tags, description, system_time, computer_name, user_id, event_id, provider_name, dbscan_cluster, raw, rule_id, rule_level, task
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (
                    alert_data['title'],
                    ','.join(alert_data['tags']),
                    alert_data['description'],
                    alert_data['SystemTime'],
                    alert_data['Computer'],
                    alert_data['TargetUserName'],
                    alert_data['EventID'],
                    alert_data['Provider_Name'],
                    None,  # Assuming dbscan_cluster is not available at this point
                    json.dumps(alert_data),
                    alert_data['id'],
                    alert_data['rule_level'],
                    alert_data['Task']
                ))
                connection.commit()
                logger.info("Inserted alert data into 'sigma_alerts'.")
    except Error as e:
        logger.error(f"Error inserting alert data: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    initialize_sql_tables()

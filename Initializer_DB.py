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
    "user": "root",
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
                    ruleid VARCHAR(50),
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
                    ruleid VARCHAR(50),
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

# Ensure columns exist
def ensure_column_exists(table_name, column_name, column_definition):
    """Ensure the specified column exists in the given table."""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'")
                result = cursor.fetchone()
                if not result:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
                    connection.commit()
                    logger.info(f"Added '{column_name}' column to '{table_name}' table.")
    except Error as e:
        logger.error(f"Error ensuring '{column_name}' column exists in '{table_name}': {e}")
    finally:
        if connection.is_connected():
            connection.close()

# Insert alert data into the sigma_alerts table
def insert_alert(alert_data):
    """Insert alert data into the sigma_alerts table."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO sigma_alerts (
                    title, tags, description, system_time, computer_name, user_id, event_id, provider_name, dbscan_cluster, raw, ruleid, rule_level, task
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (
                    alert_data.get('title'),
                    ','.join(alert_data.get('tags', [])),
                    alert_data.get('description'),
                    alert_data.get('SystemTime'),
                    alert_data.get('Computer'),
                    alert_data.get('TargetUserName'),
                    alert_data.get('EventID'),
                    alert_data.get('Provider_Name'),
                    None,  # Assuming dbscan_cluster is not available at this point
                    json.dumps(alert_data),
                    alert_data.get('id'),
                    alert_data.get('rule_level'),
                    alert_data.get('Task')
                ))
                connection.commit()
                logger.info("Inserted alert data into 'sigma_alerts'.")
    except Error as e:
        logger.error(f"Error inserting alert data: {e}")
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    initialize_sql_tables()
    ensure_column_exists("sigma_alerts", "ruleid", "VARCHAR(50)")
    ensure_column_exists("dbscan_outlier", "ruleid", "VARCHAR(50)")
    ensure_column_exists("sigma_alerts", "rule_level", "VARCHAR(50)")
    ensure_column_exists("dbscan_outlier", "rule_level", "VARCHAR(50)")
    ensure_column_exists("sigma_alerts", "task", "VARCHAR(255)")
    ensure_column_exists("dbscan_outlier", "task", "VARCHAR(255)")

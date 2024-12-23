# AnomalyHunter

AnomalyHunter is a comprehensive solution for detecting and analyzing anomalies in log files. This project includes services for MySQL database management, anomaly detection using the DBSCAN algorithm, and logging mechanisms to handle and process log data efficiently.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Services](#services)
- [Scripts](#scripts)
- [Database and Tables](#database-and-tables)
- [Log Files](#log-files)
- [Cron Job](#cron-job)
- [Contributing](#contributing)
- [License](#license)

## Installation

This section describes how to install and set up AnomalyHunter on your server.

### Prerequisites

- Ubuntu 18.04 or later
- Python 3.6 or later
- MySQL Server

### Steps

1. **Clone the repository**:
    ```sh
    git clone https://github.com/ashokchokalingam/AnomalyHunter.git
    cd AnomalyHunter
    ```

2. **Run the setup script**:
    ```sh
    sudo bash setup.sh
    ```

    The setup script will:
    - Install MySQL server and secure the installation.
    - Create a MySQL database and user.
    - Install Python 3 and pip.
    - Install required Python packages.
    - Initialize the SQL tables by running `Initializer_DB.py`.
    - Create systemd services for `SQL.py`, `dbscan.py`, and `logger.py`.
    - Set up a cron job to run `truncatesyslog.py` every hour.

## Usage

After installation, the services will be up and running. You can manage the services using systemd commands:

- Start a service:
    ```sh
    sudo systemctl start <service-name>
    ```

- Stop a service:
    ```sh
    sudo systemctl stop <service-name>
    ```

- Check the status of a service:
    ```sh
    sudo systemctl status <service-name>
    ```

The cron job will automatically run `truncatesyslog.py` every hour to truncate logs older than 24 hours.

## Services

### sql.service

- **Description**: Manages the `SQL.py` script.
- **Dependencies**: network.target

### dbscan.service

- **Description**: Manages the `dbscan.py` script.
- **Dependencies**: sql.service

### logger.service

- **Description**: Manages the `logger.py` script.
- **Dependencies**: dbscan.service

## Scripts

### setup.sh

The main setup script that installs all necessary components and sets up the services and cron job.

### Initializer_DB.py

Script to initialize the SQL tables.

### SQL.py

- **Description**: 
  - Handles SQL-related tasks such as inserting, updating, and querying the database.
  - Manages the interaction between the application and the MySQL database, ensuring data is stored and retrieved efficiently.
  - Contains functions to initialize SQL tables, ensure columns exist, read and update bookmark files, process log files, and truncate old data.

### dbscan.py

- **Description**: 
  - Performs anomaly detection using the DBSCAN (Density-Based Spatial Clustering of Applications with Noise) algorithm.
  - Processes log data to identify clusters of anomalies and helps in detecting unusual patterns that may indicate security incidents or system issues.
  - Includes functions to fetch data from the database, preprocess data, run DBSCAN clustering, and update the database with cluster labels.

### logger.py

Script to handle logging of detected anomalies.

### truncatesyslog.py

Script to truncate log files older than 24 hours.

## Database and Tables

### Database: `sigma_db`

- **Tables**:
    - `sigma_alerts`: Stores information about detected alerts.
    - `dbscan_outlier`: Stores details of detected outliers.

**Table Details**:
- **`sigma_alerts`**:
    - `id`: Unique identifier for each alert.
    - `title`: Title of the alert.
    - `tags`: Tags associated with the alert.
    - `description`: Description of the alert.
    - `system_time`: Timestamp of the alert.
    - `computer_name`: Name of the computer where the alert was generated.
    - `user_id`: User ID associated with the alert.
    - `event_id`: Event ID of the alert.
    - `provider_name`: Name of the provider generating the alert.
    - `dbscan_cluster`: Cluster value assigned by the DBSCAN algorithm.
    - `raw`: Raw log data.

- **`dbscan_outlier`**:
    - `id`: Unique identifier for each outlier.
    - `title`: Title of the outlier.
    - `tags`: Tags associated with the outlier.
    - `description`: Description of the outlier.
    - `system_time`: Timestamp of the outlier.
    - `computer_name`: Name of the computer where the outlier was generated.
    - `user_id`: User ID associated with the outlier.
    - `event_id`: Event ID of the outlier.
    - `provider_name`: Name of the provider generating the outlier.
    - `dbscan_cluster`: Cluster value assigned by the DBSCAN algorithm.
    - `raw`: Raw log data.

## Log Files

- **Location**: `/var/log/anomalyhunter/`
- **Log Files**:
    - `anomaly.syslog`: Main log file where all anomalies are recorded.

## Cron Job

A cron job is set up to run `truncatesyslog.py` every hour to maintain the log files by truncating entries older than 24 hours.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure your code follows the existing style and passes all tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

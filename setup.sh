#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Update package list
apt-get update

# Install MySQL server
apt-get install -y mysql-server

# Automatically secure MySQL installation
# Set the root password and apply security settings
debconf-set-selections <<< 'mysql-server mysql-server/root_password password sigma'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password sigma'

# Run the secure installation steps with automatic responses
mysql -u root -p'sigma' -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'sigma';"
mysql -u root -p'sigma' -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p'sigma' -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p'sigma' -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
mysql -u root -p'sigma' -e "FLUSH PRIVILEGES;"

# Create the sigma_db database and sigma user
mysql -u root -p'sigma' -e "CREATE DATABASE IF NOT EXISTS sigma_db;"
mysql -u root -p'sigma' -e "CREATE USER IF NOT EXISTS 'sigma'@'localhost' IDENTIFIED BY 'sigma';"
mysql -u root -p'sigma' -e "GRANT ALL PRIVILEGES ON sigma_db.* TO 'sigma'@'localhost';"
mysql -u root -p'sigma' -e "FLUSH PRIVILEGES;"

# Install Python3 and pip
apt-get install -y python3 python3-pip

# Install required Python packages
pip3 install -r requirements.txt

# Run the Initializer_DB.py script to initialize the SQL tables
python3 Initializer_DB.py

# Get the current directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Create the sql.service file
cat <<EOL | tee /etc/systemd/system/sql.service
[Unit]
Description=SQL Service
After=network.target

[Service]
User=root
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/SQL.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Create the dbscan.service file
cat <<EOL | tee /etc/systemd/system/dbscan.service
[Unit]
Description=DBSCAN Service
After=sql.service
Requires=sql.service

[Service]
User=root
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/dbscan.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Create the logger.service file
cat <<EOL | tee /etc/systemd/system/logger.service
[Unit]
Description=Logger Service
After=network.target
After=dbscan.service
Requires=dbscan.service

[Service]
User=root
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/logger.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Ensure truncatesyslog.py is executable
chmod +x $SCRIPT_DIR/truncatesyslog.py

# Create a cron job to run the truncatesyslog.py script every hour
crontab -l > mycron
echo "0 * * * * /usr/bin/python3 $SCRIPT_DIR/truncatesyslog.py" >> mycron
crontab mycron
rm mycron

# Reload systemd, enable and start the services
systemctl daemon-reload
systemctl enable sql.service
systemctl start sql.service
sleep 5  # Wait for 5 seconds before starting the dbscan service
systemctl enable dbscan.service
systemctl start dbscan.service
sleep 5  # Wait for 5 seconds before starting the logger service
systemctl enable logger.service
systemctl start logger.service

echo "Setup complete. MySQL server and all required Python packages have been installed. Services have been created and started. Cron job for truncatesyslog.py has been added."

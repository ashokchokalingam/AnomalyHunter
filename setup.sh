#!/bin/bash

# Update package list
sudo apt-get update

# Install MySQL server
sudo apt-get install -y mysql-server

# Automatically secure MySQL installation
# Set the root password and apply security settings
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password sigma'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password sigma'

# Run the secure installation steps with automatic responses
sudo mysql -u root -p'sigma' -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'sigma';"
sudo mysql -u root -p'sigma' -e "DELETE FROM mysql.user WHERE User='';"
sudo mysql -u root -p'sigma' -e "DROP DATABASE IF EXISTS test;"
sudo mysql -u root -p'sigma' -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
sudo mysql -u root -p'sigma' -e "FLUSH PRIVILEGES;"

# Create the sigma_db database and sigma user
sudo mysql -u root -p'sigma' -e "CREATE DATABASE IF NOT EXISTS sigma_db;"
sudo mysql -u root -p'sigma' -e "CREATE USER IF NOT EXISTS 'sigma'@'localhost' IDENTIFIED BY 'sigma';"
sudo mysql -u root -p'sigma' -e "GRANT ALL PRIVILEGES ON sigma_db.* TO 'sigma'@'localhost';"
sudo mysql -u root -p'sigma' -e "FLUSH PRIVILEGES;"

# Install Python3 and pip
sudo apt-get install -y python3 python3-pip

# Install required Python packages
pip3 install -r requirements.txt

# Get the current directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Create the sql.service file
cat <<EOL | sudo tee /etc/systemd/system/sql.service
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
cat <<EOL | sudo tee /etc/systemd/system/dbscan.service
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

# Reload systemd, enable and start the services
sudo systemctl daemon-reload
sudo systemctl enable sql.service
sudo systemctl start sql.service
sleep 5  # Wait for 5 seconds before starting the dbscan service
sudo systemctl enable dbscan.service
sudo systemctl start dbscan.service

echo "Setup complete. MySQL server and all required Python packages have been installed. Services have been created and started."

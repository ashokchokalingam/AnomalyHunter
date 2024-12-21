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

echo "Setup complete. MySQL server and all required Python packages have been installed."

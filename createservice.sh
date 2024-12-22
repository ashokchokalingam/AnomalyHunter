#!/bin/bash

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
sudo systemctl enable dbscan.service
sudo systemctl start dbscan.service

echo "Services have been created and started."

#!/bin/bash

# Define variables
APP_DIR=$(pwd)
SERVICE_NAME="falcon_mini"
DESCRIPTION="Falcon Mini"
PYTHON_EXECUTABLE="/usr/bin/python3"
SCRIPT_PATH="$APP_DIR/main.py"
WORKING_DIRECTORY="$APP_DIR"
USERNAME=rishi

# Create the service file
cat <<EOF | sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null
[Unit]
Description=$DESCRIPTION
After=network.target

[Service]
ExecStart=$PYTHON_EXECUTABLE $SCRIPT_PATH >2/dev/null
WorkingDirectory=$WORKING_DIRECTORY
Restart=always
User=$USERNAME

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Start and enable the service
sudo systemctl start $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

# Display status
sudo systemctl status $SERVICE_NAME

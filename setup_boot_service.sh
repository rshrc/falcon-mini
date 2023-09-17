#!/bin/bash

# Define variables
APP_DIR=${pwd}
SERVICE_NAME="Boot Script"
DESCRIPTION="Boot Script Service"
SCRIPT_PATH="$APP_DIR/boot_script.sh"
USERNAME=rishi

# Create the service file
cat <<EOF | sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null
[Unit]
Description=$DESCRIPTION
After=network.target

[Service]
ExecStart=$SCRIPT_PATH
Restart=always
User=$USERNAME

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Display status
sudo systemctl status $SERVICE_NAME

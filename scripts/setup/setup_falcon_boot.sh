#!/bin/bash

# Variables
WORKING_DIR=$(pwd)
SERVICE_NAME="falcon_boot"
SERVICE_DESCRIPTION="Falcon Boot Service"
PYTHON_PATH="/usr/bin/python3"
SCRIPT_PATH="$WORKING_DIR/boot_service.py"
USERNAME=root

echo $SCRIPT_PATH

# Create the service file
cat <<EOL | sudo tee /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=${SERVICE_DESCRIPTION}
After=network.target

[Service]
ExecStart=${PYTHON_PATH} ${SCRIPT_PATH}
Restart=no
User=${USERNAME}
Environment=PATH=/usr/bin:/bin:/usr/local/bin
WorkingDirectory=${WORKING_DIR}

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

echo "${SERVICE_NAME}.service created and enabled!"

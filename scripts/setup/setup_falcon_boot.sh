#!/bin/bash

# Variables
WORKING_DIR=$(realpath "$(pwd)/../../")
SERVICE_NAME="falcon_boot"
SERVICE_DESCRIPTION="Falcon Boot Service"
PYTHON_PATH="/usr/bin/python3"
# SCRIPT_PATH=$(realpath "$WORKING_DIR/../../")
USERNAME=root

echo $WORKING_DIR

# exit 1

# Create the service file
cat <<EOL | sudo tee /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=${SERVICE_DESCRIPTION}
After=network-online.target remote-fs.target
Wants=network-online.target remote-fs.target

[Service]
ExecStart=${PYTHON_PATH} -m services.boot_service
Restart=on-failure
User=${USERNAME}
Environment=PYTHONPATH=/home/rishi/falcon_mini
WorkingDirectory=${WORKING_DIR}

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

echo "${SERVICE_NAME}.service created and enabled!"

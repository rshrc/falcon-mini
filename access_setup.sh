#!/bin/bash

# Define the directory for the Flask app
APP_DIR=$(pwd)

# Create the directory if it doesn't exist
mkdir -p $APP_DIR

# Write the Flask app to a file
cat <<EOL > $APP_DIR/main.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/set-wifi-credentials', methods=['POST'])
def set_wifi_credentials():
    try:
        wifi_ssid = request.json.get('ssid')
        wifi_password = request.json.get('password')
        # with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as file:
        #     file.write(f'\\n\\nnetwork={{\\n    ssid="{wifi_ssid}"\\n    psk="{wifi_password}"\\n    key_mgmt=WPA-PSK\\n}}\\n')
        print("J3 Server Online")
        return 'Credentials updated successfully', 200

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOL

# Install Gunicorn
sudo pip3 install gunicorn

chmod +x main.py

# Create the systemd service file
cat <<EOL | sudo tee /etc/systemd/system/flask_app.service
[Unit]
Description=Flask App Service
After=network.target

[Service]
User=rishi
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/gunicorn -b 0.0.0.0:5000 main:app
Restart=on-failure
Type=simple

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
sudo systemctl enable flask_app
sudo systemctl start flask_app

# Check the status of the service
sudo systemctl status flask_app

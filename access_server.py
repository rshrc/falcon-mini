from flask import Flask, request

app = Flask(__name__)

@app.route('/api/set-wifi-credentials', methods=['POST'])
def set_wifi_credentials():
    try:
        # Assuming the request sends JSON data with keys 'ssid' and 'password'
        wifi_ssid = request.json.get('ssid')
        wifi_password = request.json.get('password')

        # Write the WiFi credentials to wpa_supplicant.conf
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as file:
            file.write(f'\n\nnetwork={{\n    ssid="{wifi_ssid}"\n    psk="{wifi_password}"\n    key_mgmt=WPA-PSK\n}}\n')

        # Optionally, trigger network reconfiguration (if required)
        # os.system('sudo systemctl restart networking')

        return 'Credentials updated successfully', 200

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the app on all available network interfaces

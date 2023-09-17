from flask import Flask, request
import os
app = Flask(__name__)

@app.route('/api/set-wifi-credentials', methods=['POST'])
def set_wifi_credentials():
    try:
        wifi_ssid = request.json.get('ssid')
        wifi_password = request.json.get('password')
      #  with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as file:
       #     file.write(f'\n\nnetwork={{\n    ssid="{wifi_ssid}"\n    psk="{wifi_password}"\n    key_mgmt=WPA-PSK\n}}\n')
        os.system("sudo echo Hello >> /etc/wpa_supplicant/wpa_supplicant.conf")
	print("J3 Server Online")
        return 'Credentials updated successfully', 200

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

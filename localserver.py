from flask import Flask, request
import os

from regex import R
app = Flask(__name__)



@app.route('/api/set-wifi-credentials', methods=['POST'])
def set_wifi_credentials():
    try:
        wifi_ssid = request.json.get('ssid')
        wifi_password = request.json.get('password')
        network_block = """
            network={
                ssid=wifi_ssid
                psk=wifi_psk
                key_mgmt=WPA-PSK
            }
        """
        network_block = network_block.replace("wifi_ssid", wifi_ssid).replace("wifi_psk", wifi_password).strip()

        # with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as file:
        # network_block = network_block.replace("Your_SSID", wifi_ssid).replace("Your_PSK_Password", wifi_password)
        os.system(f"sudo echo '{network_block}' >> /etc/wpa_supplicant/wpa_supplicant.conf")
        print("J3 Server Online")
        return f'Credentials updated successfully with {wifi_ssid} and {wifi_password}', 200

    except Exception as e:
        return str(e), 500

@app.route('/api/ping', methods=['GET'])
def ping_connection():
    return f"Product is Online", 200

@app.route('/api/restart', methods=['GET'])
def restart():
    os.system("sudo ~/LL-MAI-PI-SOFTWARE/scrap_access_point.sh")
    return "Restarted System", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

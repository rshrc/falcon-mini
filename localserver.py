import asyncio
import os

from flask import Flask, request
from icecream.icecream import IceCreamDebugger
from regex import R

from utils.writer import generate_config

app = Flask(__name__)

ic = IceCreamDebugger()

working_dir = os.getcwd()

async def run_script(script: str):
    proc = await asyncio.create_subprocess_shell(
        script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    return stdout, stderr

@app.route('/api/set-wifi-credentials', methods=['POST'])
def set_wifi_credentials():
    try:
        wifi_ssid = request.json.get('ssid')
        wifi_password = request.json.get('password')

        ic(f"Received {wifi_password}, {wifi_ssid}")

        network_block = """
            network={
                ssid=wifi_ssid
                psk=wifi_psk
                key_mgmt=WPA-PSK
            }
        """
        network_block = network_block.replace("wifi_ssid", f"\"{wifi_ssid}\"").replace("wifi_psk", f"\"{wifi_password}\"").strip()
        # remove everything below the 3rd line
        os.system("sudo sed -i '4,$d' /etc/wpa_supplicant/wpa_supplicant.conf")
        # with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as file:
        # network_block = network_block.replace("Your_SSID", wifi_ssid).replace("Your_PSK_Password", wifi_password)
        os.system(f"sudo echo '{network_block}' >> /etc/wpa_supplicant/wpa_supplicant.conf")
        print("J3 Server Online")
        return f'Credentials updated successfully with {wifi_ssid} and {wifi_password}', 200

    except Exception as e:
        ic(str(e))
        return str(e), 500

@app.route('/api/ping', methods=['GET'])
def ping_connection():
    ic("J3 Localserver pinged!")
    return f"Product is Online", 200

@app.route('/api/turn_off_hotspot', methods=['GET'])
async def turn_off_hotspot():

    stdout, stderr = await run_script("sudo ~/LL-MAI-PI-SOFTWARE/scrap_access_point.sh")

    ic(stdout, stderr)

    return "Turned Off Hotspot", 200

@app.route('/api/register_profile', methods=['POST'])
async def register_profile():
    ic("Registering Profile")

    uuid = request.json.get('uuid')
    age = request.json.get('age')






    return "registerd id", 200


@app.route('/api/restart', methods=['GET'])
def restart():
    ic("Received signal for restart")
    os.system("sudo ~/LL-MAI-PI-SOFTWARE/scrap_access_point.sh")
    return "Restarted System", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

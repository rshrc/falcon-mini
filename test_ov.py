import os
wifi_ssid = "RISHI"
wifi_password = "PASSWORd"
network_block = """
            network={
                ssid=wifi_ssid
                psk=wifi_psk
                key_mgmt=WPA-PSK
            }
        """
network_block = network_block.replace("wifi_ssid", wifi_ssid).replace("wifi_psk", wifi_password)

command = f"echo '{network_block}' | sudo tee -a test_file"

print(network_block)

os.system(command)
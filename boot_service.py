import subprocess
import time
from icecream.icecream import IceCreamDebugger
import os

ic = IceCreamDebugger()


def system_in_access_point_mode() -> bool:
    # Check the status of the hostapd service
    result = subprocess.run(['systemctl', 'is-active', 'hostapd'], capture_output=True, text=True)
    print(result.stdout.strip())
    return result.stdout.strip() == "active"

def connect_to_internet() -> bool:
    # Implement the logic to try connecting to the internet.
    # This can be a ping command or any other method you prefer.
    try:
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'])
        return True
    except subprocess.CalledProcessError:
        return False
    
dir = os.getcwd()
    
def main():
    success = False
    access_point = system_in_access_point_mode()
    print(f"Is Access Point {access_point}")
    if  not access_point:
        for _ in range(1):  
            if connect_to_internet():
                success = True
                break
            time.sleep(1)

        if success:
            print("Connected to Internet")
            subprocess.run(['sudo', 'systemctl', 'start', 'falcon_mini.service'])
        else:
            subprocess.run(["sudo", f"{dir}/setup_access_point.sh"])
            print("Turning into Mock Hotspot")
    else:
        subprocess.run(["sudo", f"{dir}/scrap_access_point.sh"])
        print("Access Point Scrapped, Turning on Wifi")

        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"])

if __name__ == "__main__":
    main()

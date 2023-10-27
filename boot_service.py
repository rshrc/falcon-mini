import os
import subprocess
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, filename='falcon_boot.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')


def system_in_access_point_mode() -> bool:
    result = subprocess.run(['systemctl', 'is-active', 'hostapd'], capture_output=True, text=True)
    logging.info(f"hostapd status: {result.stdout.strip()}")
    return result.stdout.strip() == "active"

def connect_to_internet() -> bool:
    try:
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'])
        return True
    except subprocess.CalledProcessError:
        return False

dir = os.getcwd()


def setup_access_point():
    for _ in range(5):  # Try 5 times
        if os.path.exists("/etc/hostapd/hostapd.conf"):
            subprocess.run(["sudo", f"/home/rishi/falcon_mini/scripts/setup/setup_access_point.sh"])
            break
        time.sleep(1)
    

def scrap_access_point():
    subprocess.run(["sudo", f"/home/rishi/falcon_mini/scripts/setup/scrap_access_point.sh"])

def main():
    logging.info("Main Function Is Called")

    success = False
    access_point = system_in_access_point_mode()

    

    logging.info("System Not In Access Point Mode")
    for trial in range(5):  # Try 5 times with a delay
        logging.info(f"Trying to Connect for {trial} number...")
        if connect_to_internet():
            success = True
            break
        logging.info(f"Failed to Connect....")
        time.sleep(1)

    if success:
        logging.info("Connected to Internet")

        subprocess.call(['sudo', 'systemctl', 'enable', 'falcon_mini.service'])
        
    else:
        logging.info("Turning into Mock Hotspot")
        for _ in range(5):  # Try 5 times
            if os.path.exists("/etc/hostapd/hostapd.conf"):
                logging.info("Calling setup access point script")
                subprocess.call(['sudo','/home/rishi/falcon_mini/scripts/setup/setup_access_point.sh'], )
                break
            time.sleep(1)
            sys.exit(0)
       

if __name__ == "__main__":
    main()

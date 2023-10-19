import os
import subprocess
import time
import logging
import sys
# from disply_lib import DisplayController

logging.basicConfig(level=logging.INFO, filename='falcon_boot.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# dpc = DisplayController()

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

# dir_path = os.path.dirname(os.path.realpath(__file__))
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
        # dpc.render_text_threaded_v2("Trying to connect... This may take a while.")
        if connect_to_internet():
            success = True
            break
        logging.info(f"Failed to Connect....")
        time.sleep(1)

    if success:
        logging.info("Connected to Internet")
        # dpc.render_text_threaded_v2("Connected to Internet.. Starting Talking Panda")
        # start falcon_mini from script
        subprocess.call(['sudo', 'systemctl', 'enable', 'falcon_mini.service'])
        logging.info("Line 61")
        # subprocess.call(['sudo', 'systemctl', 'restart', 'falcon_mini.service'])
        logging.info("Line 63")
        
        # os.system("sudo systemctl enable falcon_mini.service")
        # os.sytem("sudo systemctl restart falcon_mini.service")
        #subprocess.run(['sudo', '/home/rishi/falcon_mini/scripts/setup/start_falcon_mini.sh'])
        #output = subprocess.run(['sudo', 'systemctl', 'start', 'falcon_mini.service'], capture_output=True, text=True)
        # logging.info(f"For Starting Falcon Mini > {output}")
    else:
        logging.info("Turning into Mock Hotspot")
        for _ in range(5):  # Try 5 times
            if os.path.exists("/etc/hostapd/hostapd.conf"):
                logging.info("Calling setup access point script")
                subprocess.call(['sudo','/home/rishi/falcon_mini/scripts/setup/setup_access_point.sh'], )
                # subprocess.run(["sudo", '/home/rishi/falcon_mini/scripts/setup/setup_access_point.sh'])
                break
            time.sleep(1)
            # exiting script
            sys.exit(0)
        # subprocess.run(["sudo", f"/home/rishi/falcon_mini/scripts/setup/setup_access_point.sh"])
    # else:
    #     logging.info("Access Point Scrapped, Turning on Wifi")
        
    #     subprocess.call(["sudo", f"/home/rishi/falcon_mini/scripts/setup/scrap_access_point.sh"])
    #     subprocess.call(["sudo", "systemctl", "restart", "dhcpcd"])
    #     sys.exit(0)

if __name__ == "__main__":
    main()

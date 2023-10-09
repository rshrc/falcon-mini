import subprocess
import time
from icecream.icecream import IceCreamDebugger

ic = IceCreamDebugger()


def is_in_access_point_mode():
    # Check the status of the hostapd service
    result = subprocess.run(['systemctl', 'is-active', 'hostapd'], capture_output=True, text=True)
    ic(result.stdout.strip())
    return result.stdout.strip() == "active"

# Test
# if is_in_access_point_mode():
#     print("The system is in access point mode.")
# else:
#     print("The system is not in access point mode.")

def connect_to_internet():
    # Implement the logic to try connecting to the internet.
    # This can be a ping command or any other method you prefer.
    try:
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'])
        return True
    except subprocess.CalledProcessError:
        return False
    
def main():
    if is_in_access_point_mode():
        for _ in range(10):  # Try 10 times
            if connect_to_internet():
                success = True
                break
            time.sleep(1)  # Wait for 1 second

        if success:
            ic("Connected to Internet")
            # subprocess.run(['systemctl', 'start', 'falcon_mini.service'])
        else:
            # subprocess.run(['./setup_access_point.sh'])
            ic("Turning into Mock Hotspot")

if __name__ == "__main__":
    main()

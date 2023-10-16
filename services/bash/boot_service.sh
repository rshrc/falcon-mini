#!/bin/bash

# Function to check if the system is in access point mode
system_in_access_point_mode() {
    if systemctl is-active hostapd | grep -q "active"; then
        echo "true"
    else
        echo "false"
    fi
}

# Function to check internet connectivity
connect_to_internet() {
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo "true"
    else
        echo "false"
    fi
}

# Main logic
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
access_point=$(system_in_access_point_mode)

echo "Is Access Point $access_point"

if [ "$access_point" == "false" ]; then
    for _ in {1..1}; do
        if [ "$(connect_to_internet)" == "true" ]; then
            success="true"
            break
        fi
        sleep 1
    done

    if [ "$success" == "true" ]; then
        echo "Connected to Internet"
        sudo systemctl start falcon_mini.service
    else
        sudo "$DIR/setup_access_point.sh"
        echo "Turning into Mock Hotspot"
    fi
else
    sudo "$DIR/scrap_access_point.sh"
    echo "Access Point Scrapped, Turning on Wifi"
    sudo systemctl restart dhcpcd
fi

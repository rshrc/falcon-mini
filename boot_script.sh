#!/bin/bash

# Function to check internet connectivity
check_internet() {
    timeout 10 bash -c 'cat < /dev/null > /dev/tcp/google.com/80' 2>/dev/null
}

# Function to check if system is in access point mode or not

check_access_point() {
    if systemctl is-active --quiet hostapd; then
        return 0  # Return true
    else
        return 1  # Return false
    fi
}

check_network_blocks() {
    local wpa_file="/etc/wpa_supplicant/wpa_supplicant.conf"
    
    if grep -q "network={" "$wpa_file"; then
        return 0  # Return true
    else
        return 1  # Return false
    fi
}

if check_network_blocks; then
    echo "Network Block is Available"
    if check_internet; then
        # Code block to run when there is internet
        echo "Internet is available. Running in Normal Mode"

        # start falcon mini service
    else
        echo "Turning Off Access Point Mode"
        # Stop Services
        sudo systemctl stop hostapd
        sudo systemctl stop dnsmasq

        # Remove dhcpcd configuration
        sudo sed -i '/interface wlan0/,+2d' /etc/dhcpcd.conf

        # Restore original dnsmasq configuration
        sudo mv /etc/dnsmasq.conf.orig /etc/dnsmasq.conf

        # Remove hostapd configuration
        sudo rm /etc/hostapd/hostapd.conf

        # Restore original hostapd default file
        sudo sed -i 's/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/#DAEMON_CONF=""/' /etc/default/hostapd

        # Disable IP Forwarding
        sudo sed -i '/^net.ipv4.ip_forward=1/s/^/#/' /etc/sysctl.conf
        sudo sysctl -p

        # Remove NAT rules
        sudo iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
        sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

        # Remove iptables restore command from rc.local
        sudo sed -i '/iptables-restore < \/etc\/iptables.ipv4.nat/d' /etc/rc.local

        # Reboot
        sudo reboot
    # Start Falcon Mini Service
else if check_access_point; then
    echo "Device running in Access Point Mode, User Needs to Share WiFi Credentials"
else
    # Code block to run when there is no internet
    echo "Internet is not available. Turning on Access Point"
    # Add your code here
    sudo apt install hostapd dnsmasq -y

    # Stop Services
    sudo systemctl stop hostapd
    sudo systemctl stop dnsmasq


    # Configure dhcpcd
    echo -e "\ninterface wlan0\nstatic ip_address=192.168.4.1/24\nnohook wpa_supplicant" | sudo tee -a /etc/dhcpcd.conf

    # Configure dnsmasq
    sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
    echo -e "interface=wlan0\ndhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | sudo tee -a /etc/dnsmasq.conf

    # Start dnsmasq
    sudo systemctl start dnsmasq

    # Configure hostapd
    echo -e "interface=wlan0\ndriver=nl80211\nssid=TalkingPanda\nhw_mode=g\nchannel=7\nwmm_enabled=0\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=Panda1234\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | sudo tee /etc/hostapd/hostapd.conf

    # Update hostapd
    sudo sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/' /etc/default/hostapd

    # Start hostapd
    sudo systemctl unmask hostapd
    sudo systemctl enable hostapd
    sudo systemctl start hostapd

    # Enable IP Forwarding
    sudo sed -i '/^#net.ipv4.ip_forward=1/s/^#//' /etc/sysctl.conf
    sudo sysctl -p

    # Configure NAT
    sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

    # Enable iptables on startup
    sudo sed -i '$iiptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local
fi
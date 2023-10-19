#!/bin/bash

# Update and Upgrade
# sudo apt update
# sudo apt upgrade -y

# Install hostapd and dnsmasq
sudo apt install hostapd dnsmasq -y
if [ $? -ne 0 ]; then
    echo "Error installing packages. Exiting."
    exit 1
fi

# Stop Services
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Backup and Configure dhcpcd
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
printf "\ninterface wlan0\nstatic ip_address=192.168.4.1/24\nnohook wpa_supplicant" | sudo tee -a /etc/dhcpcd.conf

# Backup and Configure dnsmasq
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
printf "interface=wlan0\ndhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | sudo tee /etc/dnsmasq.conf

# Start dnsmasq
sudo systemctl start dnsmasq

# Configure hostapd
printf "interface=wlan0\ndriver=nl80211\nssid=TalkingPanda\nhw_mode=g\nchannel=7\nwmm_enabled=0\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=Panda1234\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | sudo tee /etc/hostapd/hostapd.conf

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

# Check for existence of /etc/rc.local before appending
if [ -f /etc/rc.local ]; then
    sudo sed -i '$iiptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local
else
    echo "Error: /etc/rc.local not found."
fi

# Restart services
sudo systemctl restart dhcpcd
sudo systemctl restart dnsmasq
sudo systemctl restart hostapd

# Optional: Uncomment the line below if you want to reboot after the script completes
# sudo reboot

#!/bin/bash

pwd
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# python3 $DIR/oled/lib.py --text "Turning Off Hotspot..."

# python3 $(pwd)/oled/lib.py --text "Turning Off Hotspot..."

# Stop Services
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Remove dhcpcd configuration
sudo sed -i '/interface wlan0/,+2d' /etc/dhcpcd.conf

# Restore original dnsmasq configuration
sudo mv /etc/dnsmasq.conf.orig /etc/dnsmasq.conf

# Remove hostapd configuration
# sudo rm /etc/hostapd/hostapd.conf

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
# sudo reboot
# checking if this works
sudo systemctl restart dhcpcd

# python3 $DIR/oled/lib.py --text "Toy Connected to WiFi"

# python3 $(pwd)/oled/lib.py --text "Toy Connected to WiFi"

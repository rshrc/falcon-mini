
#!/bin/bash

# Update and Upgrade
# sudo apt update
# sudo apt upgrade -y

# Install hostapd and dnsmasq
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
echo -e "interface=wlan0\ndriver=nl80211\nssid=Talking_Panda\nhw_mode=g\nchannel=7\nwmm_enabled=0\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=panda1234\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | sudo tee /etc/hostapd/hostapd.conf

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

# Reboot
sudo reboot

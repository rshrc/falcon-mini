#!/bin/bash

# Check if the user is root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Define the username for auto-login
USERNAME="rishi"

# Create the configuration file
echo "[SeatDefaults]" > /etc/lightdm/lightdm.conf.d/10-autologin.conf
echo "autologin-user=$USERNAME" >> /etc/lightdm/lightdm.conf.d/10-autologin.conf
echo "autologin-user-timeout=0" >> /etc/lightdm/lightdm.conf.d/10-autologin.conf

# Inform user and reboot
echo "Auto-login configured for user $USERNAME."
read -p "Do you want to reboot now? (y/n) " REBOOT
if [[ $REBOOT == "y" ]]; then
    reboot
else
    echo "Please reboot manually to apply the changes."
fi

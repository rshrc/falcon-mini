#!/bin/bash
# sudo sed -i '1i\deb http://mirror.mythic-beasts.com/raspbian/raspbian buster main contrib non-free rpi' /etc/apt/sources.list

# Comment out other lines if not already commented
# sudo sed -i -e '2,$s/^deb/#deb/' /etc/apt/sources.list

# Update package lists and upgrade installed packages
# sudo apt-get update
# sudo apt-get upgrade -y
sudo apt install git
# Install required packages
sudo apt-get install -y python3-pyaudio flac libsdl-ttf2.0-0 python3-sdl2 libsdl2-mixer-2.0-0 ffmpeg
sudo apt-get install python3-pygame

# Install Python Installer
sudo apt-get install python3-pip

sudo pip3 install -r requirements.txt

# Additional setup tasks (add your own commands here)
# Example: Enable SSH, configure Wi-Fi, etc.

# Reboot the Raspberry Pi for changes to take effect
# sudo reboot

# Append the export command to .bashrc
echo 'export LC_ALL=C' >> ~/.bashrc

# Source the .bashrc file to apply the changes
source ~/.bashrc
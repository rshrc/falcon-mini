#!/bin/bash

# Update package lists and upgrade installed packages
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-pyaudio flac libsdl-ttf2.0-0 python3-sdl2 libsdl2-mixer-2.0-0

# Download and install spaCy's English model
python3 -m spacy download en_core_web_sm

sudo pip3 install -r requirements.txt

# Additional setup tasks (add your own commands here)
# Example: Enable SSH, configure Wi-Fi, etc.

# Reboot the Raspberry Pi for changes to take effect
# sudo reboot
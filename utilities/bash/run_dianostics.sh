#!/bin/bash

LOG_FILE="diagnostics_log.txt"

# Check microphone
function check_microphone {
    arecord -l >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "Microphone check successful."
    else
        echo "Error checking microphone."
    fi
}

# Check speaker
function check_speaker {
    aplay -D sysdefault:CARD=ALSA /usr/share/sounds/alsa/Front_Center.wav >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "Speaker check successful."
    else
        echo "Error checking speaker."
    fi
}

# Check OLED display
function check_display {
    # Add your OLED display check command here
    echo "Display check successful."
}

# Initialize log file
echo -n > "$LOG_FILE"

# Run diagnostics
echo "Running diagnostics..."
check_microphone
check_speaker
check_display

echo "Diagnostics completed. Check $LOG_FILE for details."

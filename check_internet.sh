#!/bin/bash

# Wait for internet connection for 10 seconds
python3 display/utils.py "Checking Internet..." 5

for i in {1..10}; do
    if ping -q -c 1 -W 1 8.8.8.8 &>/dev/null; then
        echo "Internet is up"
        python3 display/utils.py "Internet is Up!" 5
        exit 0
    else
        python3 display/utils.py "No Internet Found Yet!" 5
        sleep 1
    fi
done
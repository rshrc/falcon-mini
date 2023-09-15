#!/bin/bash

# Wait for internet connection for 10 seconds
for i in {1..10}; do
    if ping -q -c 1 -W 1 8.8.8.8 &>/dev/null; then
        echo "Internet is up"
        exit 0
    else
        sleep 1
    fi
done
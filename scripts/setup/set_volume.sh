#!/bin/bash

# Waveshare Soundcard auto volume increase script
# Set 'Speaker' control to max
amixer -c 3 set 'Speaker' 127

# Set 'Speaker AC' control to max
amixer -c 3 set 'Speaker AC' 5

# Set 'Speaker DC' control to max
amixer -c 3 set 'Speaker DC' 5

#!/bin/bash

# Waveshare Soundcard auto volume increase script
# Set 'Speaker' control to max
amixer -c 1 set 'Speaker' 127

# Set 'Speaker AC' control to max
amixer -c 1 set 'Speaker AC' 5

# Set 'Speaker DC' control to max
amixer -c 1o set 'Speaker DC' 5

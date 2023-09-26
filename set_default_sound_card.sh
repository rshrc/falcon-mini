#!/bin/bash

# Define the configuration content
CONFIG_CONTENT='pcm.!default {
    type hw
    card 3
}

ctl.!default {
    type hw
    card 3
}'

# Write the content to ~/.asoundrc
echo "$CONFIG_CONTENT" > ~/.asoundrc

# Print a message to indicate success
echo "Updated ~/.asoundrc with default card set to 3."

#!/bin/bash

# Add /sbin to the PATH variable temporarily for the current session
export PATH=$PATH:/sbin

# Ask for the username
read -p "Enter the username: " username

# Path to the .bashrc file in the user's home directory
user_home=$(eval echo ~$username)
bashrc_file="$user_home/.bashrc"

# Check if the user exists
if id "$username" &>/dev/null; then
    echo "User $username exists."

    # Check if the entry already exists in the bashrc file
    if grep -Fxq 'export PATH=$PATH:/sbin' "$bashrc_file"; then
        echo "The entry already exists in the $bashrc_file file."
    else
        # Add the entry at the end of the .bashrc file
        echo 'export PATH=$PATH:/sbin' >> "$bashrc_file"
        echo "Added to the .bashrc file."
    fi
else
    echo "User $username does not exist. Check the username and try again."
fi

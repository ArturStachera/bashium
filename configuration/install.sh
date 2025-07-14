#!/bin/bash

# Function to display a question and wait for the user's response
ask_question(){
    local answer
    printf "\e[33m%s\e[0m (y/n): " "$1"
    while true; do
        read -rsn1 answer
        if [[ $answer =~ ^[yYnN]$ ]]; then
            printf "%s " "$answer" # print the answer without a newline
            break
        fi
    done
    echo "" # move to a newline
    if [[ $answer == [yY] ]]; then
        return 0
    else
        return 1
    fi
}

# User questions
clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Do you want to configure the /sbin directory?"; then
    sbin=true
fi

if [[ $sbin ]]; then
    ./sbin.sh
fi
read -rsn1 -p "Press Enter to continue..."

clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Do you want to disable the 'beep' sound?"; then
    beep=true
fi
read -rsn1 -p "Press Enter to continue..."

clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Do you want to configure Bluetooth?"; then
    bluetooth=true
fi
read -rsn1 -p "Press Enter to continue..."

clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Do you want to install drivers?"; then
    firmware=true
fi
read -rsn1 -p "Press Enter to continue..."
clear

# Run the appropriate scripts
if [[ $firmware ]]; then
    ./firmware.sh
fi

if [[ $beep ]]; then
    ./beep.sh
fi

if [[ $bluetooth ]]; then
    ./bluetooth.sh
fi


echo "Successfully completed. Please restart your computer."

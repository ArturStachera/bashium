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

clear
printf "\e[34m%s\e[0m\n" "Installing firmware packages"

if ask_question "Do you want to install INTEL WiFi drivers?"; then
    intel=true
fi
read -rsn1 -p "Press Enter to continue..."
clear

printf "\e[34m%s\e[0m\n" "Installing firmware packages"

if ask_question "Do you want to install Broadcom WiFi drivers?"; then
    broadcom=true
fi
read -rsn1 -p "Press Enter to continue..."
clear

printf "\e[34m%s\e[0m\n" "Installing firmware packages"

if ask_question "Do you want to install Realtek drivers?"; then
    realtek=true
fi
read -rsn1 -p "Press Enter to continue..."
clear

printf "\e[34m%s\e[0m\n" "Installing firmware packages"

if ask_question "Do you want to install Nvidia drivers?"; then
    nvidia=true
fi
read -rsn1 -p "Press Enter to continue..."
clear

printf "\e[34m%s\e[0m\n" "Installing firmware packages"

if ask_question "Do you want to install Non-free drivers?"; then
    nonfree=true
fi
read -rsn1 -p "Press Enter to continue..."
clear

# Install the appropriate firmware packages based on the responses
if [[ $intel ]]; then
    echo "Installing INTEL WiFi driver..."
    sudo apt install firmware-iwlwifi -y
fi

if [[ $broadcom ]]; then
    echo "Installing Broadcom WiFi driver..."
    sudo apt install firmware-brcm80211 -y
fi

if [[ $realtek ]]; then
    echo "Installing Realtek driver..."
    sudo apt install firmware-realtek -y
fi

if [[ $nvidia ]]; then
    echo "Installing Nvidia driver..."
    sudo apt install nvidia-driver linux-headers-amd64 firmware-misc-nonfree -y
fi

if [[ $nonfree ]]; then
    echo "Installing Non-free driver..."
    sudo apt install firmware-misc-nonfree firmware-linux-nonfree -y
fi

echo "Firmware installation complete."
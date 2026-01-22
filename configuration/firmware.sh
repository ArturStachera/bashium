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
    echo "Configuring NVIDIA graphics..."
    bash ./nvidia.sh
fi

if [[ $nonfree ]]; then
    echo "Installing Non-free driver..."
    target_suite=""
    if apt-cache policy firmware-misc-nonfree 2>/dev/null | grep -q "bpo"; then
        codename=$( . /etc/os-release 2>/dev/null; echo "${VERSION_CODENAME:-}" )
        if [[ -n $codename ]]; then
            target_suite="${codename}-backports"
        fi
    fi

    if [[ -n $target_suite ]]; then
        sudo apt install -y -t "$target_suite" firmware-misc-nonfree firmware-linux-nonfree amd64-microcode
    else
        sudo apt install -y firmware-misc-nonfree firmware-linux-nonfree amd64-microcode
    fi
fi

echo "Firmware installation complete."
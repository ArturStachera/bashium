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

has_nonfree_enabled(){
    if grep -Rqs -- 'non-free' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
        return 0
    fi
    return 1
}

ensure_non_free_components(){
    local changed=false

    if [[ -f /etc/apt/sources.list.d/debian.sources ]]; then
        if ! sudo grep -q "^[[:space:]]*Components:.*non-free" /etc/apt/sources.list.d/debian.sources; then
            sudo sed -i -E 's/^(Components:[[:space:]]*)(.*)$/\1\2 contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
            changed=true
        fi
    fi

    if [[ -f /etc/apt/sources.list ]]; then
        if sudo grep -Eq '^[[:space:]]*deb[[:space:]].*[[:space:]]main([[:space:]]|$)' /etc/apt/sources.list; then
            if ! sudo grep -Eq '^[[:space:]]*deb[[:space:]].*[[:space:]](main.*non-free|main.*non-free-firmware|main.*contrib)' /etc/apt/sources.list; then
                sudo sed -i -E 's/^(deb[[:space:]].*[[:space:]]main)([[:space:]]*)$/\1 contrib non-free non-free-firmware\2/' /etc/apt/sources.list
                changed=true
            fi
        fi
    fi

    if [[ $changed == true ]]; then
        sudo apt-get update
    fi
}

detect_wifi_vendors(){
    local hw
    hw=$( (command -v lspci >/dev/null 2>&1 && lspci -nn) 2>/dev/null; (command -v lsusb >/dev/null 2>&1 && lsusb) 2>/dev/null )

    wifi_intel=false
    wifi_broadcom=false
    wifi_realtek=false
    wifi_atheros=false
    wifi_mediatek=false
    wifi_ralink=false

    if echo "$hw" | grep -Eqi 'Network controller|Wireless|Wi-Fi|802\.11'; then
        if echo "$hw" | grep -Eqi 'Intel|8086:'; then wifi_intel=true; fi
        if echo "$hw" | grep -Eqi 'Broadcom|BCM|14e4:'; then wifi_broadcom=true; fi
        if echo "$hw" | grep -Eqi 'Realtek|RTL|10ec:|0bda:'; then wifi_realtek=true; fi
        if echo "$hw" | grep -Eqi 'Atheros|Qualcomm|168c:|0cf3:'; then wifi_atheros=true; fi
        if echo "$hw" | grep -Eqi 'MediaTek|Mediatek|MTK|14c3:|0e8d:'; then wifi_mediatek=true; fi
        if echo "$hw" | grep -Eqi 'Ralink|148f:'; then wifi_ralink=true; fi
    fi
}

has_nvidia_gpu(){
    if command -v lspci >/dev/null 2>&1; then
        lspci -nn | grep -qi nvidia
        return $?
    fi
    return 1
}

clear
printf "\e[34m%s\e[0m\n" "Installing firmware packages"

detect_wifi_vendors

if [[ $wifi_intel == true ]] && ask_question "Detected Intel Wi-Fi. Install firmware-iwlwifi?"; then
    intel=true
fi

if [[ $wifi_broadcom == true ]] && ask_question "Detected Broadcom Wi-Fi. Install firmware-brcm80211?"; then
    broadcom=true
fi

if [[ $wifi_realtek == true ]] && ask_question "Detected Realtek Wi-Fi. Install firmware-realtek?"; then
    realtek=true
fi

if [[ $wifi_atheros == true ]] && ask_question "Detected Atheros/Qualcomm Wi-Fi. Install firmware-atheros?"; then
    atheros=true
fi

if [[ $wifi_mediatek == true ]] && ask_question "Detected MediaTek Wi-Fi. Install firmware-mediatek?"; then
    mediatek=true
fi

if [[ $wifi_ralink == true ]] && ask_question "Detected Ralink Wi-Fi. Install firmware-ralink?"; then
    ralink=true
fi

if [[ $wifi_intel == false && $wifi_broadcom == false && $wifi_realtek == false && $wifi_atheros == false && $wifi_mediatek == false && $wifi_ralink == false ]]; then
    echo "No Wi-Fi hardware detected."
fi

if ask_question "Install non-free firmware bundle (firmware-linux-nonfree)?"; then
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

if [[ $atheros ]]; then
    echo "Installing Atheros/Qualcomm WiFi firmware..."
    sudo apt install firmware-atheros -y
fi

if [[ $mediatek ]]; then
    echo "Installing MediaTek WiFi firmware..."
    sudo apt install firmware-mediatek -y
fi

if [[ $ralink ]]; then
    echo "Installing Ralink WiFi firmware..."
    sudo apt install firmware-ralink -y
fi

if [[ $nonfree ]]; then
    echo "Installing Non-free driver..."
    if ! has_nonfree_enabled; then
        ensure_non_free_components
    else
        echo "Non-free components already enabled in APT sources."
    fi
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
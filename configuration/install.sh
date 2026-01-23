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

print_header(){
    clear
    cat <<'EOF'
+----------------------------------------------------------+
|                       BASHIUM CONFIG                     |
+----------------------------------------------------------+
EOF
}

print_status_table(){
    local wifi_status="$1"
    local bt_status="$2"
    local nvidia_status="$3"
    local nonfree_status="$4"
    local beep_status="$5"
    local sbin_status="$6"

    cat <<EOF
+----------------------+-------------------------------+
| Component            | Status                        |
+----------------------+-------------------------------+
| Wi-Fi                | ${wifi_status}
| Bluetooth            | ${bt_status}
| NVIDIA GPU           | ${nvidia_status}
| APT non-free         | ${nonfree_status}
| PC speaker beep      | ${beep_status}
| /sbin in user PATH   | ${sbin_status}
+----------------------+-------------------------------+
EOF
}

has_nonfree_enabled(){
    if grep -Rqs -- 'non-free' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
        return 0
    fi
    return 1
}

is_beep_disabled(){
    if grep -Rqs -- '^[[:space:]]*blacklist[[:space:]]\+pcspkr[[:space:]]*$' /etc/modprobe.d 2>/dev/null; then
        return 0
    fi
    if grep -q '^[[:space:]]*blacklist[[:space:]]\+pcspkr[[:space:]]*$' /etc/modprobe.d/blacklist.conf 2>/dev/null; then
        return 0
    fi
    return 1
}

user_has_sbin_in_bashrc(){
    local username="$1"
    if [[ -z $username ]]; then
        return 2
    fi
    if ! id "$username" &>/dev/null; then
        return 2
    fi
    local user_home
    user_home=$(eval echo ~"$username" 2>/dev/null)
    if [[ -z $user_home ]]; then
        return 2
    fi
    local bashrc_file="$user_home/.bashrc"
    if [[ -f $bashrc_file ]] && grep -Fxq 'export PATH=$PATH:/sbin' "$bashrc_file"; then
        return 0
    fi
    return 1
}

has_bluetooth(){
    if command -v rfkill >/dev/null 2>&1; then
        if rfkill list 2>/dev/null | grep -qi bluetooth; then
            return 0
        fi
    fi

    if command -v lspci >/dev/null 2>&1; then
        if lspci 2>/dev/null | grep -qi bluetooth; then
            return 0
        fi
    fi

    if command -v lsusb >/dev/null 2>&1; then
        if lsusb 2>/dev/null | grep -qi bluetooth; then
            return 0
        fi
    fi

    if [[ -d /sys/class/bluetooth ]]; then
        if ls /sys/class/bluetooth 2>/dev/null | grep -q '^hci'; then
            return 0
        fi
    fi

    return 1
}

has_nvidia_gpu(){
    if command -v lspci >/dev/null 2>&1; then
        lspci -nn 2>/dev/null | grep -qi nvidia
        return $?
    fi
    return 1
}

has_wifi(){
    local hw
    hw=$( (command -v lspci >/dev/null 2>&1 && lspci -nn) 2>/dev/null; (command -v lsusb >/dev/null 2>&1 && lsusb) 2>/dev/null )
    echo "$hw" | grep -Eqi 'Network controller|Wireless|Wi-Fi|802\.11'
}

# User questions
print_header

wifi_status="not detected"
bt_status="not detected"
nvidia_status="not detected"
nonfree_status="not enabled"
beep_status="enabled"
sbin_status="unknown (no user selected)"

if has_wifi; then wifi_status="detected"; fi
if has_bluetooth; then bt_status="detected"; fi
if has_nvidia_gpu; then nvidia_status="detected"; fi
if has_nonfree_enabled; then nonfree_status="enabled"; fi
if is_beep_disabled; then beep_status="disabled"; fi

read -r -p "Enter username for user-level checks (optional, press Enter to skip): " username
if [[ -n $username ]]; then
    user_has_sbin_in_bashrc "$username"
    rc=$?
    if [[ $rc -eq 0 ]]; then
        sbin_status="already configured"
    elif [[ $rc -eq 1 ]]; then
        sbin_status="not configured"
    else
        sbin_status="unknown (invalid user)"
    fi
fi

print_status_table "$wifi_status" "$bt_status" "$nvidia_status" "$nonfree_status" "$beep_status" "$sbin_status"
echo ""
echo "Select what you want to configure. You will only be prompted for relevant items."
echo ""

if [[ -n $username ]]; then
    if [[ $sbin_status == "not configured" ]]; then
        if ask_question "Configure /sbin PATH entry for the selected user?"; then
            sbin=true
        fi
    elif [[ $sbin_status == "already configured" ]]; then
        if ask_question "/sbin PATH entry seems already configured. Run anyway?"; then
            sbin=true
        fi
    else
        if ask_question "Configure /sbin PATH entry (will ask again for username)?"; then
            sbin=true
        fi
    fi
else
    if ask_question "Configure /sbin PATH entry (will ask for username)?"; then
        sbin=true
    fi
fi

if [[ $sbin ]]; then
    if [[ -n ${username:-} ]]; then
        ./sbin.sh "$username"
    else
        ./sbin.sh
    fi
fi
read -rsn1 -p "Press Enter to continue..."

print_header

if is_beep_disabled; then
    if ask_question "PC speaker beep is already disabled. Run beep disable step anyway?"; then
        beep=true
    fi
else
    if ask_question "Disable the PC speaker beep sound?"; then
        beep=true
    fi
fi
read -rsn1 -p "Press Enter to continue..."

print_header

if has_bluetooth; then
    if ask_question "Bluetooth controller detected. Configure Bluetooth?"; then
        bluetooth=true
    fi
else
    echo "No Bluetooth controller detected. Skipping Bluetooth section."
    read -rsn1 -p "Press Enter to continue..."
fi
read -rsn1 -p "Press Enter to continue..."

print_header

if has_wifi; then
    if ask_question "Detected Wi-Fi hardware that may need firmware. Install drivers/firmware now?"; then
        firmware=true
    fi
else
    echo "No Wi-Fi hardware detected. Skipping firmware section."
    read -rsn1 -p "Press Enter to continue..."
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

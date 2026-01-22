#!/bin/bash

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

if ! has_bluetooth; then
    echo "No Bluetooth controller detected."
    exit 0
fi

sudo apt install blueman -y
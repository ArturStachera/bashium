#!/bin/bash

ask_question(){
    local answer
    printf "\e[33m%s\e[0m (y/n): " "$1"
    while true; do
        read -rsn1 answer
        if [[ $answer =~ ^[yYnN]$ ]]; then
            printf "%s " "$answer"
            break
        fi
    done
    echo ""
    if [[ $answer == [yY] ]]; then
        return 0
    else
        return 1
    fi
}

if [[ $EUID -ne 0 ]]; then
    exec sudo -E bash "$0" "$@"
fi

get_codename(){
    if [[ -r /etc/os-release ]]; then
        . /etc/os-release
        if [[ -n ${VERSION_CODENAME:-} ]]; then
            echo "$VERSION_CODENAME"
            return 0
        fi
    fi
    if command -v lsb_release >/dev/null 2>&1; then
        lsb_release -sc
        return 0
    fi
    echo ""
}

get_debian_track(){
    local policy
    policy=$(apt-cache policy 2>/dev/null || true)
    if echo "$policy" | grep -q 'a=unstable'; then
        echo "unstable"
        return 0
    fi
    if echo "$policy" | grep -q 'a=testing'; then
        echo "testing"
        return 0
    fi
    if echo "$policy" | grep -q 'a=stable'; then
        echo "stable"
        return 0
    fi
    echo "unknown"
}

has_backports_enabled(){
    if grep -Rqs -- '-backports' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
        return 0
    fi
    return 1
}

has_nonfree_enabled(){
    if grep -Rqs -- 'non-free' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
        return 0
    fi
    return 1
}

apt_update(){
    DEBIAN_FRONTEND=noninteractive apt-get update
}

has_nvidia_gpu(){
    if ! command -v lspci >/dev/null 2>&1; then
        return 1
    fi
    lspci -nn | grep -qi "nvidia"
}

ensure_non_free_components(){
    local changed=false

    if [[ -f /etc/apt/sources.list.d/debian.sources ]]; then
        if ! grep -q "^[[:space:]]*Components:.*non-free" /etc/apt/sources.list.d/debian.sources; then
            sed -i -E 's/^(Components:[[:space:]]*)(.*)$/\1\2 contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources
            changed=true
        fi
    fi

    if [[ -f /etc/apt/sources.list ]]; then
        if grep -Eq '^[[:space:]]*deb[[:space:]].*[[:space:]]main([[:space:]]|$)' /etc/apt/sources.list; then
            if ! grep -Eq '^[[:space:]]*deb[[:space:]].*[[:space:]](main.*non-free|main.*non-free-firmware|main.*contrib)' /etc/apt/sources.list; then
                sed -i -E 's/^(deb[[:space:]].*[[:space:]]main)([[:space:]]*)$/\1 contrib non-free non-free-firmware\2/' /etc/apt/sources.list
                changed=true
            fi
        fi
    fi

    if [[ $changed == true ]]; then
        apt_update
    fi
}

enable_backports_if_missing_pkg(){
    local pkg="$1"
    local codename="$2"
    local track="$3"

    if [[ -z $pkg || -z $codename ]]; then
        return 1
    fi

    if [[ $track == "unstable" ]]; then
        return 1
    fi

    if apt-cache policy "$pkg" 2>/dev/null | grep -q "Candidate: (none)"; then
        local backports_file="/etc/apt/sources.list.d/bashium-backports.list"
        if [[ ! -f $backports_file ]] || ! grep -q "${codename}-backports" "$backports_file"; then
            echo "deb http://deb.debian.org/debian ${codename}-backports main contrib non-free non-free-firmware" >> "$backports_file"
        fi
        apt_update
        return 0
    fi

    return 1
}

get_recommended_driver_pkg(){
    local pkg
    pkg=""

    if command -v nvidia-detect >/dev/null 2>&1; then
        pkg=$(nvidia-detect 2>/dev/null | grep -oE 'nvidia-(driver(-[0-9]+)?|legacy-[0-9]+xx-driver)' | head -n1)
    fi

    if [[ -z $pkg ]]; then
        pkg="nvidia-driver"
    fi

    echo "$pkg"
}

blacklist_nouveau(){
    local file="/etc/modprobe.d/blacklist-nouveau.conf"
    cat > "$file" <<'EOF'
blacklist nouveau
options nouveau modeset=0
EOF
}

update_initramfs_if_available(){
    if command -v update-initramfs >/dev/null 2>&1; then
        update-initramfs -u
    fi
}

try_unload_nouveau(){
    if lsmod 2>/dev/null | grep -q '^nouveau\b'; then
        echo "Detected loaded nouveau module. Attempting to unload it (may fail if in use)..."
        modprobe -r nouveau 2>/dev/null || true
    fi
}

unblacklist_nouveau(){
    rm -f /etc/modprobe.d/blacklist-nouveau.conf
    update_initramfs_if_available
}

install_proprietary(){
    local codename="$1"
    local track="$2"

    ensure_non_free_components

    blacklist_nouveau
    try_unload_nouveau

    DEBIAN_FRONTEND=noninteractive apt-get install -y nvidia-detect

    local pkg
    pkg=$(get_recommended_driver_pkg)

    enable_backports_if_missing_pkg "$pkg" "$codename" "$track"

    if [[ -n $codename ]] && apt-cache policy "$pkg" 2>/dev/null | grep -q "${codename}-backports"; then
        DEBIAN_FRONTEND=noninteractive apt-get install -y -t "${codename}-backports" "$pkg" linux-headers-amd64 firmware-misc-nonfree
    else
        DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg" linux-headers-amd64 firmware-misc-nonfree
    fi

    update_initramfs_if_available

    echo "NVIDIA proprietary driver installation complete. Reboot is recommended."
}

configure_nouveau(){
    unblacklist_nouveau

    if ask_question "Remove proprietary NVIDIA packages if they are installed?"; then
        DEBIAN_FRONTEND=noninteractive apt-get purge -y 'nvidia-*' || true
        DEBIAN_FRONTEND=noninteractive apt-get autoremove -y || true
    fi

    echo "Nouveau configuration complete. Reboot is recommended."
}

if ! has_nvidia_gpu; then
    echo "No NVIDIA GPU detected (via lspci)."
    exit 0
fi

clear
printf "\e[34m%s\e[0m\n" "NVIDIA graphics setup"

echo "NVIDIA GPU detected."

if ask_question "Use proprietary NVIDIA driver (recommended for performance)?"; then
    codename=$(get_codename)
    track=$(get_debian_track)
    backports="no"
    nonfree="no"
    if has_backports_enabled; then backports="yes"; fi
    if has_nonfree_enabled; then nonfree="yes"; fi

    echo "Detected Debian track: $track"
    echo "Backports enabled: $backports"
    echo "Non-free enabled: $nonfree"

    install_proprietary "$codename" "$track"
else
    configure_nouveau
fi

#!/bin/bash
print_header(){
    clear
    cat <<'EOF'
+----------------------------------------------------------+
|                   BASHIUM BEEP DISABLE                    |
+----------------------------------------------------------+
EOF
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

print_header

if is_beep_disabled; then
    echo "Status: beep already disabled (pcspkr blacklisted)."
    exit 0
fi

echo "Status: beep enabled. Disabling..."

if ! sudo grep -q '^blacklist pcspkr$' /etc/modprobe.d/blacklist.conf 2>/dev/null; then
    sudo sh -c 'echo "blacklist pcspkr" >> /etc/modprobe.d/blacklist.conf'
fi

if is_beep_disabled; then
    echo "Status: beep disabled."
else
    echo "Status: unable to confirm beep disable."
fi

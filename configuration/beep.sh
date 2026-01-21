#!/bin/bash
if ! sudo grep -q '^blacklist pcspkr$' /etc/modprobe.d/blacklist.conf 2>/dev/null; then
    sudo sh -c 'echo "blacklist pcspkr" >> /etc/modprobe.d/blacklist.conf'
fi

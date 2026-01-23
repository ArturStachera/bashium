#!/bin/bash

# Add /sbin to the PATH variable temporarily for the current session
export PATH=$PATH:/sbin

print_header(){
    clear
    cat <<'EOF'
+----------------------------------------------------------+
|                     BASHIUM /SBIN PATH                   |
+----------------------------------------------------------+
EOF
}

print_header

username="${1:-}"
if [[ -z $username ]]; then
    read -r -p "Enter the username: " username
fi

# Path to the .bashrc file in the user's home directory
user_home=$(eval echo ~$username)
bashrc_file="$user_home/.bashrc"

# Check if the user exists
if ! id "$username" &>/dev/null; then
    echo "User $username does not exist. Check the username and try again."
    exit 1
fi

echo "User $username exists."

# Check if the entry already exists in the bashrc file
if grep -Fxq 'export PATH=$PATH:/sbin' "$bashrc_file" 2>/dev/null; then
    echo "Status: already configured in $bashrc_file"
    exit 0
fi

echo 'export PATH=$PATH:/sbin' >> "$bashrc_file"
echo "Status: added to $bashrc_file"

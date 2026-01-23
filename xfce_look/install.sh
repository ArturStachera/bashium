#!/bin/bash

# Find the path to the directory where the script is lockated
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header(){
    clear
    cat <<'EOF'
+----------------------------------------------------------+
|                      BASHIUM XFCE LOOK                    |
+----------------------------------------------------------+
EOF
}

count_zip(){
    local dir="$1"
    if [[ -d $dir ]]; then
        find "$dir" -maxdepth 1 -type f -name '*.zip' 2>/dev/null | wc -l
        return 0
    fi
    echo 0
}

print_status_table(){
    local username="$1"
    local icons_count="$2"
    local themes_count="$3"
    local wallpapers_count="$4"

    cat <<EOF
+----------------------+-------------------------------+
| Component            | Status                        |
+----------------------+-------------------------------+
| Username             | ${username}
| Icons zips           | ${icons_count}
| Themes zips          | ${themes_count}
| Wallpapers zips      | ${wallpapers_count}
+----------------------+-------------------------------+
EOF
}

# Ask for the username
print_header
read -p "Enter the username: " USERNAME

# Determine the user's home directory
HOME_DIR="/home/$USERNAME"

# Check if the home directory exists
if [ ! -d "$HOME_DIR" ]; then
    echo "The home directory for the user $USERNAME does not exist."
    exit 1
fi

print_header
icons_count=$(count_zip "$SCRIPT_DIR/icons")
themes_count=$(count_zip "$SCRIPT_DIR/themes")
wallpapers_count=$(count_zip "$SCRIPT_DIR/wallpapers")
print_status_table "$USERNAME" "$icons_count" "$themes_count" "$wallpapers_count"
echo ""

# Determine the paths to the .themes, .wallpapers and .icons directories
THEMES_DIR="$HOME_DIR/.themes"
WALLPAPERS_DIR="$HOME_DIR/.wallpapers"
ICONS_DIR="$HOME_DIR/.icons"

# Create these directories if they don't exist
mkdir -p "$THEMES_DIR"
mkdir -p "$WALLPAPERS_DIR"
mkdir -p "$ICONS_DIR"

# Unzip .zip files to the appropriate directories
for dir in icons themes wallpapers; do
    if [ -d "$SCRIPT_DIR/$dir" ]; then
        cd "$SCRIPT_DIR/$dir"
        for zip_file in *.zip; do
            if [ -f "$zip_file" ]; then
                echo "Unzipping $zip_file to $HOME_DIR/.$dir"
                unzip -o "$zip_file" -d "$HOME_DIR/.$dir"
            fi
        done
    fi
done

echo "Installation completed."

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
|                      BASHIUM SOFTWARE                    |
+----------------------------------------------------------+
EOF
}

print_status_table(){
    local codecs_status="$1"
    local compilation_status="$2"
    local multimedia_status="$3"
    local extra_status="$4"

    cat <<EOF
+----------------------+-------------------------------+
| Component            | Selected                      |
+----------------------+-------------------------------+
| Codecs               | ${codecs_status}
| Compilation tools    | ${compilation_status}
| Multimedia apps      | ${multimedia_status}
| Extra tools          | ${extra_status}
+----------------------+-------------------------------+
EOF
}

# User questions
print_header

if ask_question "Configure audio/video codecs?"; then
    codecs=true
fi
read -rsn1 -p "Press Enter to continue..."

print_header

if ask_question "Install compilation tools?"; then
    compilation=true
fi
read -rsn1 -p "Press Enter to continue..."

print_header

if ask_question "Configure multimedia?"; then
    multimedia=true
fi
read -rsn1 -p "Press Enter to continue..."

print_header

if ask_question "Configure additional elements?"; then
    extra=true
fi
read -rsn1 -p "Press Enter to continue..."
print_header

codecs_status="no"
compilation_status="no"
multimedia_status="no"
extra_status="no"
if [[ $codecs ]]; then codecs_status="yes"; fi
if [[ $compilation ]]; then compilation_status="yes"; fi
if [[ $multimedia ]]; then multimedia_status="yes"; fi
if [[ $extra ]]; then extra_status="yes"; fi

print_status_table "$codecs_status" "$compilation_status" "$multimedia_status" "$extra_status"
echo ""


# Run the appropriate scripts
if [[ $codecs ]]; then
    ./codecs.sh
fi

if [[ $compilation ]]; then
    ./compilation.sh
fi

if [[ $multimedia ]]; then
    ./multimedia.sh
fi

if [[ $extra ]]; then
    ./extra.sh
fi

echo "Configuration completed."


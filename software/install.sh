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

# User questions
clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Configure audio/video codecs?"; then
    codecs=true
fi
read -rsn1 -p "Press Enter to continue..."

clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Install compilation tools?"; then
    compilation=true
fi
read -rsn1 -p "Press Enter to continue..."

clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Configure multimedia?"; then
    multimedia=true
fi
read -rsn1 -p "Press Enter to continue..."

clear
printf "\e[34m%s\e[0m\n" "Debian Configuration"

if ask_question "Configure additional elements?"; then
    extra=true
fi
read -rsn1 -p "Press Enter to continue..."
clear


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


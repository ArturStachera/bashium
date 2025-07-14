#!/bin/bash

cd "$(dirname "$0")"

if [ ! -d env ]; then
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
else
    source env/bin/activate
fi

nohup python3 main.py >/dev/null 2>&1 &
disown
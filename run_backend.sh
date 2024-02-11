#! /bin/bash

if [ "main" == "$1" ]; then
    PYTHONPATH=.: python backend/main.py
elif [ "sd" == "$1" ]; then
    PYTHONPATH=.: python backend/servers/sd_server.py
else
    echo "no matched keyword"
fi
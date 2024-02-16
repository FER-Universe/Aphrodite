#! /bin/bash

if [ "chat" == "$1" ]; then
    PYTHONPATH=.: python backend/main.py
elif [ "draw" == "$1" ]; then
    PYTHONPATH=.: python backend/servers/draw_server.py
else
    echo "no matched keyword"
fi
#! /bin/bash

if [ "draw" == "$1" ]; then
    PYTHONPATH=.: streamlit run frontend/draw.py --server.headless=true --server.port=$2
elif [ "chat" == "$1" ]; then
    PYTHONPATH=.: streamlit run frontend/chat.py --server.headless=true --server.port=$2 -- --mode $3
elif [ "communicate" == "$1" ]; then
    PYTHONPATH=.: streamlit run frontend/communicate.py --server.headless=true --server.port=$2
else
    echo "no matched keyword"
fi
#! /bin/bash

if [ "draw" == "$1" ]; then
    PYTHONPATH=.: streamlit run frontend/draw.py
elif [ "chat" == "$1" ]; then
    PYTHONPATH=.: streamlit run frontend/chat.py
elif [ "communicate" == "$1" ]; then
    PYTHONPATH=.: streamlit run frontend/communicate.py
else
    echo "no matched keyword"
fi
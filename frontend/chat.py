import argparse

import streamlit as st
from settings import (
    DEFAULT_COLOR_IMAGE,
)
from visualize import visualize_color_image, visualize_facial_image, flicker_color_img
from request import request_writer_api
import argparse
import numpy as np
import time


def show_streamlit_title(role):
    st.title(f"💬 Chat with your {role} BOT")


def main(role):
    show_streamlit_title(role)

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []
        st.session_state.current_emotion = "Neutral"

    col1, col2 = st.columns(2)

    if prompt := st.chat_input("Input your message."):
        response, va_emotion, discrete_emotion = request_writer_api(prompt, role)

        with st.chat_message("ai", avatar="🤖"):
            st.session_state.messages.append(
                {
                    "role": "🧝",
                    "content": prompt,
                }
            )
            st.session_state.messages.append(
                {
                    "role": "🤖",
                    "content": response,
                }
            )

        with col1:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with col2:
            st.header(discrete_emotion)
            emo_image = st.image(
                DEFAULT_COLOR_IMAGE,
                caption="Emotion status",
                width=200,
            )
            visualize_facial_image(
                emo_image, st.session_state.current_emotion, discrete_emotion
            )
            st.session_state.current_emotion = discrete_emotion
            # if you want the color image to flicker continuously with white noise, add this line
            # flicker_color_img(emo_image, st.session_state.current_emotion)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatbot")

    parser.add_argument(
        "--mode",
        type=str,
        default="psychotherapist",
        help="Persona for your chatbot to talk to",
    )
    args = parser.parse_args()
    main(args.mode)

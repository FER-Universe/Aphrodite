import argparse

import streamlit as st
from file import (
    ANGRY_FILE_PATH,
    HAPPY_FILE_PATH,
    NEUTRAL_FILE_PATH,
    PLEASED_FILE_PATH,
    SAD_FILE_PATH,
)
from request import request_writer_api


def show_streamlit_title(role):
    st.title(f"💬 Chat with your {role} BOT")


def main(role):
    show_streamlit_title(role)

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []

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

            if "Happy" in discrete_emotion:
                st.image(HAPPY_FILE_PATH)
            elif "Peaceful" in discrete_emotion:
                st.image(PLEASED_FILE_PATH)
            elif "Angry" in discrete_emotion:
                st.image(ANGRY_FILE_PATH)
            elif "Sad" in discrete_emotion:
                st.image(SAD_FILE_PATH)
            elif "Neutral" in discrete_emotion:
                st.image(NEUTRAL_FILE_PATH)


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

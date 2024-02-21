import streamlit as st
from request import request_writer_api
import argparse


def show_streamlit_title(role):
    st.title(f"💬 Chat with your {role} BOT")


def main(role):
    show_streamlit_title(role)

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []

    if prompt := st.chat_input("입력 프롬프트"):
        response, emotion_va, emotion_dis = request_writer_api(prompt, role)

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
                    "content": response
                    + f"(지금 기분: VA; ({emotion_va}), LABEL: {emotion_dis}",
                }
            )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


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

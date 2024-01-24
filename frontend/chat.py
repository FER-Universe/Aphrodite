import streamlit as st
from request import request_writer_api


def show_streamlit_title():
    st.title("Aphrodite (chat)")


def main():
    show_streamlit_title()

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []

    if prompt := st.chat_input("입력 프롬프트"):
        response, emotion = request_writer_api(prompt)

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
                    "content": response + "(지금 기분(VA): " + emotion + ")",
                }
            )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if __name__ == "__main__":
    main()

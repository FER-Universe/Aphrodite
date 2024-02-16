import streamlit as st
from request import request_writer_api


def show_streamlit_title():
    st.title("💬 Chat with your BOT")


def main():
    show_streamlit_title()

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []

    col1, col2 = st.columns(2)

    if prompt := st.chat_input("Input your message."):
        response, va_emotion, discrete_emotion = request_writer_api(prompt)

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
                    # + f"(지금 기분: VA; ({va_emotion}), LABEL: {discrete_emotion}",
                    + f" (EMOTION LABEL: {discrete_emotion})",
                }
            )

        with col1:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with col2:
            st.header(discrete_emotion)

            if "Happy" in discrete_emotion:
                st.image("./assets/happy.png")
            elif "Peaceful" in discrete_emotion:
                st.image("./assets/happy.png")
            elif "Angry" in discrete_emotion:
                st.image("./assets/angry.png")
            elif "Sad" in discrete_emotion:
                st.image("./assets/sad.png")
            elif "Neutral" in discrete_emotion:
                st.image("./assets/neutral.png")


if __name__ == "__main__":
    main()

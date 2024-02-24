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
import argparse
import numpy as np
import time


@st.cache_data
def load_image_setting():
    color_map = {
        "Happy": np.array([230, 230, 0]),
        "Sad": np.array([0, 0, 230]),
        "Angry": np.array([230, 0, 0]),
        "Peaceful": np.array([0, 230, 0]),
        "Neutral": np.array([128]),
    }

    normal_image = np.ones((100, 100, 3), dtype=np.uint8)
    return color_map, normal_image


def show_streamlit_title(role):
    st.title(f"💬 Chat with your {role} BOT")


def main(role):
    show_streamlit_title(role)

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []
        color_map, _ = load_image_setting()
        st.session_state.from_emotion = color_map["Neutral"]

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
            color_map, normal_image = load_image_setting()

            def change_color(from_emotion, to_emotion):
                from_img, to_img = (
                    normal_image * from_emotion,
                    normal_image * to_emotion,
                )
                for i in np.linspace(0, 1, 51):
                    noise = np.random.randint(25, size=np.shape(normal_image))
                    yield (to_img * i + from_img * (1 - i)).astype(np.uint8) + noise

            emo_image = st.image(
                normal_image * st.session_state.from_emotion,
                caption="Emotion status",
                width=200,
            )
            to_emotion = [
                color_map[key] for key in color_map.keys() if key in discrete_emotion
            ][0]
            if not (st.session_state.from_emotion == to_emotion).all():
                for color_img in change_color(
                    st.session_state.from_emotion, to_emotion
                ):
                    emo_image.image(color_img, caption="Emotion status", width=200)
                    time.sleep(0.1)

                st.session_state.from_emotion = to_emotion

            while True:
                noise = np.random.randint(25, size=np.shape(normal_image))
                color_img = normal_image * st.session_state.from_emotion + noise
                emo_image.image(color_img, caption="Emotion status", width=200)
                time.sleep(0.1)


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

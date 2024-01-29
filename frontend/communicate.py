import glob

import streamlit as st
from PIL import Image
from request import request_clip_matching_api, request_stt_api, request_writer_api


def show_streamlit_title():
    st.title("Aphrodite (communicate)")


def main():
    show_streamlit_title()

    if "session" not in st.session_state:
        st.session_state.session = 1
        st.session_state.messages = []

    st.button("Reset", type="primary")
    if st.button("Record Your Voice for communicate Aphrodite..."):
        st.write("You touched button...")
        response = request_stt_api()
        print("response: ", response)

    if st.button("show image"):
        with open("converted_text.txt", "r") as f:
            converted_text = f.read()
        top_1_idx = request_clip_matching_api(converted_text)
        print("top_1_idx: ", top_1_idx)
        # top_1_idx = "1"

        face_image_path = glob.glob(
            "C:/Users/DaehaKim/Desktop/Research/Aphrodite/backend/assets/*"
        )

        st.image(
            Image.open(face_image_path[int(top_1_idx)]), caption="selected facial image"
        )

    # if prompt := st.chat_input("입력 프롬프트"):
    #     response, emotion = request_writer_api(prompt)

    #     with st.chat_message("ai", avatar="🤖"):
    #         st.session_state.messages.append(
    #             {
    #                 "role": "🧝",
    #                 "content": prompt,
    #             }
    #         )
    #         st.session_state.messages.append(
    #             {
    #                 "role": "🤖",
    #                 "content": response + "(지금 기분(VA): " + emotion + ")",
    #             }
    #         )

    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])


if __name__ == "__main__":
    main()

import glob
import os

import requests
import streamlit as st
from PIL import Image
from streamlit.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":

    st.title("🎨 Draw your MIND")
    if "prompt" not in st.session_state:
        st.session_state["prompt"] = "N/A"

    with st.sidebar:
        st.write("__Prompt__")
        st.info(st.session_state.prompt)

    st.button("Reset", type="primary")

    if prompt := st.chat_input("Input your thinking to draw."):
        st.session_state.prompt = prompt

        with st.sidebar:
            st.write("__Prompt__")
            st.info(st.session_state.prompt)

        r = requests.post("http://127.0.0.1:8000", data=prompt)
        logger.info(r)

    if st.button("Show image"):
        list_of_files = glob.glob("D:/Research/assets/imgs/pixels/*")
        latest_file = max(list_of_files, key=os.path.getctime)

        img = Image.open(latest_file)
        st.image(img)

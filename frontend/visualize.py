from settings import (
    FACIAL_MAP,
    COLOR_MAP,
    COLOR_IMAGE_SIZE,
    DEFAULT_COLOR_IMAGE,
)
import time
from PIL import Image
import numpy as np


def change_image(from_emotion, to_emotion, mode="facial"):
    if mode == "facial":
        from_img, to_img = Image.open(from_emotion), Image.open(to_emotion)
        for i in np.linspace(0, 1, 31):
            yield Image.blend(from_img, to_img, alpha=i)

    elif mode == "color":
        from_img, to_img = (
            DEFAULT_COLOR_IMAGE * from_emotion,
            DEFAULT_COLOR_IMAGE * to_emotion,
        )
        for i in np.linspace(0, 1, 31):
            noise = np.random.randint(25, size=COLOR_IMAGE_SIZE)
            yield (to_img * i + from_img * (1 - i)).astype(np.uint8) + noise


def visualize_facial_image(image_state, from_emotion, to_emotion):
    from_emotion_path = [
        FACIAL_MAP[key] for key in FACIAL_MAP.keys() if key in from_emotion
    ][0]
    to_emotion_path = [
        FACIAL_MAP[key] for key in FACIAL_MAP.keys() if key in to_emotion
    ][0]

    if from_emotion != to_emotion:
        for image in change_image(from_emotion_path, to_emotion_path, mode="facial"):
            image_state.image(image, caption="Emotion status", width=200)
            time.sleep(0.05)
    else:
        image_state.image(to_emotion_path, caption="Emotion status", width=200)


def visualize_color_image(image_state, from_emotion, to_emotion):
    from_emotion_color = [
        COLOR_MAP[key] for key in COLOR_MAP.keys() if key in from_emotion
    ][0]
    to_emotion_color = [
        COLOR_MAP[key] for key in COLOR_MAP.keys() if key in to_emotion
    ][0]

    if from_emotion != to_emotion:
        for image in change_image(from_emotion_color, to_emotion_color, mode="color"):
            image_state.image(image, caption="Emotion status", width=200)
            time.sleep(0.05)


def flicker_color_img(image_state, emotion):
    emotion_color = [COLOR_MAP[key] for key in COLOR_MAP.keys() if key in emotion][0]
    while True:
        noise = np.random.randint(25, size=COLOR_IMAGE_SIZE)
        color_img = DEFAULT_COLOR_IMAGE * emotion_color + noise
        image_state.image(color_img, caption="Emotion status", width=200)
        time.sleep(0.05)

import numpy as np

PREFIX = "./assets"

HAPPY_FILE_PATH = PREFIX + "/emotion_templates/happy.png"
PLEASED_FILE_PATH = PREFIX + "/emotion_templates/pleased.png"
ANGRY_FILE_PATH = PREFIX + "/emotion_templates/angry.png"
SAD_FILE_PATH = PREFIX + "/emotion_templates/sad.png"
NEUTRAL_FILE_PATH = PREFIX + "/emotion_templates/neutral.png"

FAICAL_IMAGE_SIZE = (1024, 1024, 3)

FACIAL_MAP = {
    "Happy": HAPPY_FILE_PATH,
    "Sad": SAD_FILE_PATH,
    "Angry": ANGRY_FILE_PATH,
    "Pleased": PLEASED_FILE_PATH,
    "Neutral": NEUTRAL_FILE_PATH,
}

COLOR_IMAGE_SIZE = (100, 100, 3)

COLOR_MAP = {
    "Happy": np.array([230, 230, 0]),
    "Sad": np.array([0, 0, 230]),
    "Angry": np.array([230, 0, 0]),
    "Pleased": np.array([0, 230, 0]),
    "Neutral": np.array([128]),
}

DEFAULT_COLOR_IMAGE = np.ones(COLOR_IMAGE_SIZE, dtype=np.uint8)

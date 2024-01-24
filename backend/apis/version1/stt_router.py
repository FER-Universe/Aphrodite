import os
import time
from datetime import datetime
from typing import Dict

import playsound
import requests
import speech_recognition as sr
from fastapi import APIRouter
from gtts import gTTS


def speak(text):
    tts = gTTS(text=text, lang="ko")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = " "

        try:
            said = r.recognize_google(audio, language="ko-KR")
        except Exception as e:
            pass

    return said


router = APIRouter(prefix="/api")


@router.get("/stt")
async def convert_string_to_text(is_repeat: bool = True) -> Dict[str, str]:
    if os.path.isfile("converted_text.txt"):
        os.remove("converted_text.txt")

    speak("안녕하세요. 2초 후에 말씀하시고, 종료시 '굿바이'라고 말씀하시면 됩니다.")

    while True:
        text = get_audio()
        print(text)

        if is_repeat:
            tts = gTTS(text=text, lang="ko")
            filename = "user_voice.mp3"
            tts.save(filename)
            playsound.playsound(filename)

        with open("converted_text.txt", "a") as f:
            f.write(str(text) + "\n")

        if "굿바이" in text:
            break

        time.sleep(0.1)
    return {"message": "ok"}

import ast
import json
from typing import List, Optional

import requests

import os, sys

sys.path.append(
    os.path.abspath(os.path.join("backend", ".."))
)  # 이게 먼저 선언이 안되면 아래 모듈 import 가 안됨

from backend.configs.config import settings

if settings.IS_DEFAULT_PATH:
    sys.path.append(os.path.abspath(os.path.join("backend", "..")))


def request_touch_api():
    return "Touch!"


def request_stt_api():
    prefix = "http://" if settings.IS_PREFIX else ""
    api_url = (
        f"{prefix}{settings.IP_ADDRESS}:{settings.PORT}/{settings.STT_API}".strip()
    )
    return requests.get(api_url)


def request_clip_matching_api(converted_text: str):
    prefix = "http://" if settings.IS_PREFIX else ""
    print("converted_text: ", converted_text)

    data = {"converted_text": converted_text}
    api_url = f"{prefix}{settings.IP_ADDRESS}:{settings.PORT}/{settings.CLIP_MATCHING_API}".strip()
    return json.loads(requests.post(api_url, json=data).text)["top_1_idx"]


def request_writer_api(prompt: Optional[str] = None):
    if prompt == "hello":
        prefix = "http://" if settings.IS_PREFIX else ""
        api_url = f"{prefix}{settings.IP_ADDRESS}:{settings.PORT}/{settings.BASIC_API}".strip()
        print(api_url)
        return (ast.literal_eval(requests.get(api_url).text)["message"], "", "")
    else:
        session_request = {"title_nm": prompt}
        prefix = "http://" if settings.IS_PREFIX else ""
        if settings.IS_EMOTION:
            api_url = f"{prefix}{settings.IP_ADDRESS}:{settings.PORT}/{settings.EMOTION_API}".strip()
        else:
            api_url = (
                f"{prefix}{settings.IP_ADDRESS}:{settings.PORT}/{settings.ADVANCED_API}"
            ).strip()
        print(api_url)
        result = ast.literal_eval(requests.post(api_url, json=session_request).text)
        response = result["openai_msg_ctt"]
        if settings.IS_EMOTION:
            emotion_va, emotion_dis = result["emotion_va"], result["emotion_dis"]
        else:
            emotion_va, emotion_dis = "", ""
        return response, emotion_va, emotion_dis

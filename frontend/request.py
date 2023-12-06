import ast
from typing import List, Optional

import requests

from backend.configs.config import settings


def request_writer_api(prompt: Optional[str] = None):
    if prompt == "hello":
        return ast.literal_eval(
            requests.get(
                f"{settings.IP_ADDRESS}:{settings.PORT}/{settings.BASIC_API}"
            ).text
        )["message"]
    else:
        session_request = {"title_nm": prompt}
        result = ast.literal_eval(
            requests.post(
                f"{settings.IP_ADDRESS}:{settings.PORT}/{settings.EMOTION_API}",
                json=session_request,
            ).text
        )
        response = result["openai_msg_ctt"]
        emotion = result["emotion"]
        return response, emotion

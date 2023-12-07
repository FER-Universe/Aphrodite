import ast
from typing import List, Optional

import requests

# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join("backend", "..")))
from backend.configs.config import settings


def request_writer_api(prompt: Optional[str] = None):
    if prompt == "hello":
        return (
            ast.literal_eval(
                requests.get(
                    f"http://{settings.IP_ADDRESS}:{settings.PORT}/{settings.BASIC_API}"
                ).text
            )["message"],
            "",
        )
    else:
        session_request = {"title_nm": prompt}
        result = ast.literal_eval(
            requests.post(
                f"http://{settings.IP_ADDRESS}:{settings.PORT}/{settings.ADVANCED_API}",
                json=session_request,
            ).text
        )
        print(result)
        response = result["openai_msg_ctt"]
        # emotion = result["emotion"]
        emotion = ""
        return response, emotion

import json
import time
from threading import Semaphore

import openai
import requests
from fastapi import APIRouter

from apis.data.database import add_message_to_db
from configs.config import settings
from schemas.gpt_sch import GptRequestSch, GptResponseSch, GptResponseSch_msgonly

sem = Semaphore(3)
router = APIRouter(prefix="/api/openai")


@router.post("/translate/by/gpt", response_model=GptResponseSch_msgonly)
async def translate_by_gpt_router(req: GptRequestSch):
    openai_result = await translate_by_openai(req)

    add_message_to_db(openai_result)

    return {
        "openai_msg_ctt": openai_result,
    }


async def translate_by_openai(req: GptRequestSch):
    with sem:
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": req.title_nm + "한국어로 100자 이내로 말해 줘."}
            ],
            "temperature": 0.7,
            "max_tokens": 512,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=settings.OPENAI_HEADERS,
            json=data,
        )
        output = json.loads(response.text)
        print("output: ", output)
        openai_result = output["choices"][0]["message"]["content"]

        time.sleep(1)

    return openai_result

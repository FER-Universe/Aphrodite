import json
import time
from threading import Semaphore

import openai
import requests
from configs.config import settings
from fastapi import APIRouter
from schemas.gpt_sch import GptRequestSch, GptResponseSch

sem = Semaphore(3)

router = APIRouter(prefix="/api/openai")


@router.post("/translate/by/gpt", response_model=GptResponseSch)
async def translate_by_gpt_router(req: GptRequestSch):
    openai_result = await translate_by_openai(req)
    # bard_result = await translate_by_bard(req)

    return {
        "openai_msg_ctt": openai_result,
        # "bard_msg_ctt": bard_result,
    }


async def translate_by_openai(req: GptRequestSch):
    with sem:
        data = {
            "model": "gpt-3.5-turbo",
            # "messages": [{"role": "user", "content": req.title_nm + "한국어로 100자 이내로 설명해줘"}],
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


# async def translate_by_bard(req: GptRequestSch):
#     bard = Bard(token=settings.BARD_API_KEY)
#     bard_result = bard.get_answer(req.title_nm + '한국어로 100자 이내로 설명해줘')['content']
#     return bard_result

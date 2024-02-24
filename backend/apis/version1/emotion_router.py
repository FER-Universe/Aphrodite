import glob
import json
import logging
import time
from threading import Semaphore

import clip
import openai
import requests
import torch
from deep_translator import GoogleTranslator
from fastapi import APIRouter
from PIL import Image

from configs.config import settings
from schemas.gpt_sch import GptRequestSch, GptResponseSch
from utils.fer_util import (
    map_discrete_emotion_from_va,
    nn_output,
    normalize_feature,
    set_models,
)

logger = logging.getLogger(__name__)

translator = GoogleTranslator(source="ko", target="en")


sem = Semaphore(3)

router = APIRouter(prefix="/api/openai")


@router.post("/response_with_emotion", response_model=GptResponseSch)
async def translate_by_gpt_router(req: GptRequestSch):
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model_type: str = "ViT-B/32"
    img_path_for_glob: str = "./assets/emotion_templates/*"

    openai_result = await chat_with_openai(req)

    trans_result = translator.translate(text=req.title_nm)
    # openai_result = await translate_by_openai(req)

    logger.info("openai result: " + openai_result)
    logger.info("translated result: " + trans_result)

    face_image_path = glob.glob(img_path_for_glob)
    model, preprocess = clip.load(clip_model_type, device=device)
    encoder, regressor, header = set_models(device)

    try:
        text = clip.tokenize([trans_result]).to(device)
    except RuntimeError:
        text = clip.tokenize([trans_result.split(",").split(" ")[-1]]).to(device)

    with torch.no_grad():
        text_feature = normalize_feature(model.encode_text(text))  # shape: [1, 512]

    image_feature_list = []
    for i in range(len(face_image_path)):
        image = preprocess(Image.open(face_image_path[i])).unsqueeze(0).to(device)
        with torch.no_grad():
            image_feature = normalize_feature(model.encode_image(image))
            image_feature_list.append(image_feature)
    image_features = torch.vstack(image_feature_list)  # shape: [N, 512]

    similarity = (100.0 * image_features @ text_feature.T).softmax(dim=0)

    top_1_idx = torch.argmax(similarity)
    logger.info("selected: " + face_image_path[top_1_idx])
    foo = preprocess(Image.open(face_image_path[top_1_idx])).unsqueeze(0).to(device)

    latent_feature = encoder(foo)
    va_output = header(regressor(latent_feature))
    valence, arousal = va_output[0, 0].item(), va_output[0, 1].item()
    emotion_va = str(round(valence, 4)) + "," + str(round(arousal, 4))
    emotion_dis = map_discrete_emotion_from_va(valence, arousal)
    logger.info("emotion_va: ", emotion_va)
    logger.info("emotion_dis: ", emotion_dis)
    logger.info("openai result: ", openai_result)

    return {
        "openai_msg_ctt": openai_result,
        "emotion_va": emotion_va,
        "emotion_dis": emotion_dis,
    }


async def translate_by_openai(req: GptRequestSch):
    with sem:
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": req.title_nm + "10단어 이내로 짧게 말해 줘.",
                }
            ],
            "temperature": 0.7,
            "max_tokens": 128,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=settings.OPENAI_HEADERS,
            json=data,
        )
        output = json.loads(response.text)
        logger.info("output: ", output)
        openai_result = output["choices"][0]["message"]["content"]

    return openai_result


async def chat_with_openai(req: GptRequestSch):
    with sem:
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": f"As a friendly {req.role}, respond in a natural way to the user's words below.\n\n{req.title_nm}",
                }
            ],
            "temperature": 0.7,
            "max_tokens": 128,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=settings.OPENAI_HEADERS,
            json=data,
        )
        output = json.loads(response.text)
        logger.info("output: ", output)
        openai_result = output["choices"][0]["message"]["content"]

    return openai_result

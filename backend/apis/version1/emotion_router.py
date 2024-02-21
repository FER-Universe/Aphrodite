import glob
import json
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
from utils.fer_util import nn_output

translator = GoogleTranslator(source="ko", target="en")


def normalize_feature(input_tensor: torch.Tensor):
    return input_tensor / input_tensor.norm(dim=-1, keepdim=True)


def set_models(device: str):
    encoder, regressor, header = nn_output()

    encoder.load_state_dict(
        torch.load("backend/weights/enc2.t7", map_location=torch.device(device)),
        strict=False,
    )
    regressor.load_state_dict(
        torch.load("backend/weights/reg2.t7", map_location=torch.device(device)),
        strict=False,
    )
    header.load_state_dict(
        torch.load("backend/weights/header2.t7", map_location=torch.device(device)),
        strict=False,
    )

    encoder.eval()
    regressor.eval()
    header.eval()
    return encoder, regressor, header


def map_discrete_emotion_from_va(valence: float, arousal: float):
    """
    Map emotions from continuous(va-domain) to discrete label(Happy, Sad, Neutral, Angry)
    The mapping is based on quadrants, with a distance of 0.3 or less defined as "Neutral".
    Args:
        valence(float): The degree to which an emotion is positive or negative, [-1,1]
        arousal(float): Level of emotional excitement, [-1,1]

    Output:
        emotion class(str): one of ["Happy", "Sad", "Neutral", "Angry", "Peaceful"]
    """
    result = ""
    emotion_strength = torch.norm(torch.FloatTensor([valence, arousal]))
    if emotion_strength <= 0.15:
        result = "Neutral"
        return result
    elif emotion_strength > 0.15 and emotion_strength < 0.3:
        result = "Slightly "
    elif emotion_strength >= 0.7:
        result = "Very "

    if valence >= 0 and arousal >= 0:
        result += "Happy"
    elif valence >= 0 and arousal < 0:
        result += "Peaceful"
    elif valence < 0 and arousal >= 0:
        result += "Angry"
    else:
        result += "Sad"

    return result


sem = Semaphore(3)

router = APIRouter(prefix="/api/openai")


@router.post("/response_with_emotion", response_model=GptResponseSch)
async def translate_by_gpt_router(req: GptRequestSch):
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    # translation: google translator로 변경 / openai_result -> trans_result
    # openai_result = await translate_by_openai(req)
    print("raw input: " + req.title_nm)

    openai_result = await chat_with_openai(req)
    print("openai result: " + openai_result)
    trans_result = translator.translate(text=req.title_nm)
    print("translated result: " + trans_result)
    # load models
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    encoder, regressor, header = set_models(device)

    face_image_path = glob.glob("./backend/assets/*")

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
    print("selected: " + face_image_path[top_1_idx])
    foo = preprocess(Image.open(face_image_path[top_1_idx])).unsqueeze(0).to(device)

    latent_feature = encoder(foo)
    va_output = header(regressor(latent_feature))
    valence, arousal = va_output[0, 0].item(), va_output[0, 1].item()
    emotion_va = str(round(valence, 4)) + "," + str(round(arousal, 4))
    emotion_dis = map_discrete_emotion_from_va(valence, arousal)
    print("\n\nemotion_va: ", emotion_va)
    print("\n\nemotion_dis: ", emotion_dis)
    print("\n\nopenai result: ", openai_result)

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
        print("output: ", output)
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
        print("output: ", output)
        openai_result = output["choices"][0]["message"]["content"]

    return openai_result

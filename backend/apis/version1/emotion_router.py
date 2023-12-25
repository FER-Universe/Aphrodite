import glob
import json
import time
from threading import Semaphore

import clip
import openai
import requests
import torch
from fastapi import APIRouter
from PIL import Image

from configs.config import settings
from schemas.gpt_sch import GptRequestSch, GptResponseSch
from utils.fer_util import nn_output


def normalize_feature(input_tensor: torch.Tensor):
    return input_tensor / input_tensor.norm(dim=-1, keepdim=True)


def set_models():
    encoder, regressor, header = nn_output()

    encoder.load_state_dict(torch.load("backend/weights/enc2.t7"), strict=False)
    regressor.load_state_dict(torch.load("backend/weights/reg2.t7"), strict=False)
    header.load_state_dict(torch.load("backend/weights/header2.t7"), strict=False)

    encoder.eval()
    regressor.eval()
    header.eval()
    return encoder, regressor, header


sem = Semaphore(3)

router = APIRouter(prefix="/api/openai")


@router.post("/response_with_emotion", response_model=GptResponseSch)
async def translate_by_gpt_router(req: GptRequestSch):
    device: str = "cuda"
    openai_result = await translate_by_openai(req)

    # load models
    model, preprocess = clip.load("ViT-B/32", device=device)
    encoder, regressor, header = set_models()

    face_image_path = glob.glob(
        "C:/Users/DaehaKim/Desktop/Research/Aphrodite/backend/assets/*"
    )

    try:
        text = clip.tokenize([str(openai_result)]).to(device)
    except RuntimeError:
        text = clip.tokenize([str(openai_result).split(",").split(" ")[-1]]).to(device)

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

    foo = preprocess(Image.open(face_image_path[top_1_idx])).unsqueeze(0).to(device)

    latent_feature = encoder(foo)
    va_output = header(regressor(latent_feature))
    emotion = str(va_output[0, 0].item()) + "," + str(va_output[0, 1].item())
    print("\n\nemotion: ", emotion)
    print("\n\nopenai result: ", openai_result)

    return {
        "openai_msg_ctt": openai_result,
        "emotion": emotion,
    }


async def translate_by_openai(req: GptRequestSch):
    with sem:
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": req.title_nm + "10단어 이내로 짧게 말해 줘."}
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

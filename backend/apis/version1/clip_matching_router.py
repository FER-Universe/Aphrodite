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
from pydantic import BaseModel

from configs.config import settings
from schemas.gpt_sch import GptRequestSch, GptResponseSch


from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="ko", target="en")


class CLIPRequestSch(BaseModel):
    converted_text: str

    class Config:
        orm_mode = True
        schema_extra = {"example": {"converted_text": "Your texturized voice..."}}


def normalize_feature(input_tensor: torch.Tensor):
    return input_tensor / input_tensor.norm(dim=-1, keepdim=True)


router = APIRouter(prefix="/api")


@router.post("/clip_matching")
async def translate_by_gpt_router(req: CLIPRequestSch):
    device: str = "cuda"
    face_image_path = glob.glob("./backend/assets/*")

    # load models
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)
    model, preprocess = clip.load("ViT-B/32", device=device)
    """Modified by Dohee Kang 
    # Before 
    try:
        text = clip.tokenize([req.converted_text]).to(device)
    except RuntimeError:
        text = clip.tokenize([req.converted_text.split(",").split(" ")[-1]]).to(device)
    """
    # After
    try:
        raw_text = req.converted_text.rstrip(" 굿바이\n")
        raw_text = translator.translate(text=raw_text)
        print(f"input text: {raw_text}")
        text = clip.tokenize([raw_text]).to(device)
    except RuntimeError:
        text = clip.tokenize([raw_text.split(",").split(" ")[-1]]).to(device)

    with torch.no_grad():
        text_feature = normalize_feature(model.encode_text(text))

    image_feature_list = []
    for i in range(len(face_image_path)):
        image = preprocess(Image.open(face_image_path[i])).unsqueeze(0).to(device)
        with torch.no_grad():
            image_feature = normalize_feature(model.encode_image(image))
            image_feature_list.append(image_feature)
    image_features = torch.vstack(image_feature_list)
    print("\nimage_features.shape: ", image_features.shape)

    similarity = (100.0 * image_features @ text_feature.T).softmax(dim=0)
    print("\nsimilarity: ", similarity)

    top_1_idx = torch.argmax(similarity)
    return {"top_1_idx": str(top_1_idx.cpu().numpy())}

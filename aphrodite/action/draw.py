import os

import PIL

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"

import torch
from aphrodite.action import Action
from diffusers import StableDiffusionPipeline


class Draw(Action):
    def __init__(self) -> None:
        super().__init__()

    def save_images(self, images: PIL, save_path: str = "") -> None:
        images.save(save_path)

    def generate_images(
        self,
        device: str,
        prompt: str,
        model_name_or_path: str = "CompVis/stable-diffusion-v1-4",
        img_shape: tuple = None,
    ) -> None:
        model_opt = {
            "torch.dtype": "torch.float16",
            "revision": "fp16",
            "device": device,
            # safety_checker=None,
            # requires_safety_checker=False,
        }
        pipe = StableDiffusionPipeline.from_pretrained(
            model_name_or_path,
            **model_opt,
        ).enable_attention_slicing()

        if img_shape is not None:
            image = pipe(prompt, height=img_shape[0], width=img_shape[1]).images[0]
        else:
            image = pipe(prompt).images[0]
        return image


if __name__ == "__main__":
    device = "cpu"
    prompt = ""
    model_name_or_path = "CompVis/stable-diffusion-v1-4"

    draw = Draw()
    image = draw.generate_images(
        device=device,
        model_name_or_path=model_name_or_path,
        prompt=prompt,
    )

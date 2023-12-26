import gc
import os
import platform
from typing import Dict

import PIL

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"

import torch
from aphrodite.action import Action
from aphrodite.util import MODEL_CONFIG
from diffusers import (
    AutoPipelineForText2Image,
    DiffusionPipeline,
    DPMSolverSinglestepScheduler,
    StableDiffusionPipeline,
    StableDiffusionXLPipeline,
)
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl_img2img import (
    StableDiffusionXLImg2ImgPipeline,
)


class GreatDraw(Action):
    def __init__(self, model_name: str) -> None:
        super().__init__()

        self._model_name = model_name

    def save_images(self, images: PIL, save_path: str = "./image.png") -> None:
        images.save(save_path)

    def generate_images(
        self,
        model_config: Dict[str, Dict],
        prompt: str,
        negative_prompt: str,
        refine_img: bool = False,
        save_img: bool = True,
    ) -> None:
        if model_config[self._model_name]["type"] == "name":
            pipe = StableDiffusionXLPipeline.from_single_file(
                model_config[self._model_name]["name"],
                **model_config["pipe_opt"],
            ).to(device)
        elif model_config[self._model_name]["type"] == "path":
            pipe = AutoPipelineForText2Image.from_pretrained(
                model_config[self._model_name]["path"],
                **model_config["pipe_opt"],
            )
        else:
            raise TypeError(
                f"Invalid model type {model_config[self._model_name]['type']}"
            )

        if torch.__version__ > "2.0.0" and platform.system() != "Windows":
            pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
        pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config)

        if refine_img:
            refiner = DiffusionPipeline.from_pretrained(
                model_config["sdxl-refiner"]["path"],
                text_encoder_2=pipe.text_encoder_2,
                vae=pipe.vae,
                **model_config["pipe_opt"],
            )

        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            **model_config["inference_opt"],
        ).images[0]

        if refine_img:
            image = self._refine_image(refiner, image, prompt)

        if save_img:
            self.save_images(image)

        gc.collect()
        torch.cuda.empty_cache()
        return image

    def _refine_image(
        self,
        refiner: StableDiffusionXLImg2ImgPipeline,
        image: PIL,
        prompt: str,
        num_inference_steps: int = 25,
        high_noise_frac: float = 0.8,
    ) -> PIL:
        return refiner(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            high_noise_frac=high_noise_frac,
            image=image,
        ).images[0]


if __name__ == "__main__":
    prompt = ""
    negative_prompt = ""

    draw = GreatDraw(model_name="sdxl-realistic")

    image = draw.generate_images(
        model_config=MODEL_CONFIG,
        prompt=prompt,
        negative_prompt=negative_prompt,
    )
    print("finished to draw image!!!")

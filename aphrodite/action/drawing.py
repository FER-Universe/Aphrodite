import base64
import gc
import os
import platform
from datetime import datetime
from io import BytesIO
from typing import Dict, Optional

import PIL

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"

import torch
from aphrodite.action import DrawingBase
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
from transformers import CLIPTextModel


class Drawing(DrawingBase):
    def __init__(self, model_name: str, model_config: Dict[str, Dict]) -> None:
        super().__init__()

        self._model_name = model_name
        self._model_config = model_config
        self._max_token_length = model_config["max_token_length"]
        self._device = model_config["device"]

    def _resize_text_encoder(self) -> None:
        if self._model_config["clip_skip"] > 1:
            text_encoder = CLIPTextModel.from_pretrained(
                self._model_config["sdxl-turbo"]["path"],
                subfolder="text_encoder",
                num_hidden_layers=12 - (self._model_config["clip_skip"] - 1),
                torch_dtype=torch.float16,
            ).to(self._device)
            self._model_config["sdxl-turbo"]["pipe_opt"]["text_encoder"] = text_encoder

    def get_pipe(
        self, use_lora_weights: bool = False
    ) -> StableDiffusionPipeline | StableDiffusionXLPipeline:
        self._resize_text_encoder()

        if self._model_config[self._model_name]["type"] == "name":
            pipe = StableDiffusionXLPipeline.from_single_file(
                self._model_config[self._model_name]["name"],
                **self._model_config[self._model_name]["pipe_opt"],
            )
        elif self._model_config[self._model_name]["type"] == "path":
            pipe = AutoPipelineForText2Image.from_pretrained(
                self._model_config[self._model_name]["path"],
                **self._model_config[self._model_name]["pipe_opt"],
            )
        else:
            raise TypeError(
                f"Invalid model type {self._model_config[self._model_name]['type']}"
            )
        print("[INFO] Loaded SD model.")

        if use_lora_weights:
            pipe.load_lora_weights(self._model_config[self._model_name]["lora_path"])
            print(
                f"[INFO] Lora weights: {self._model_config[self._model_name]['lora_path'].split('/')[-1].split('.')[0]}"
            )
            print("[INFO] Loaded LoRa weights.")

        if torch.__version__ > "2.0.0" and platform.system() != "Windows":
            pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
        pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config)
        print(f"[INFO] Loaded scheduler {pipe.scheduler}")
        return pipe

    def _get_refiner(
        self, pipe: StableDiffusionPipeline | StableDiffusionXLPipeline
    ) -> StableDiffusionXLImg2ImgPipeline:
        refiner = DiffusionPipeline.from_pretrained(
            self._model_config["sdxl-refiner"]["path"],
            text_encoder_2=pipe.text_encoder_2,
            vae=pipe.vae,
            **self._model_config[self._model_name]["pipe_opt"],
        )
        return refiner

    def __refine(
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

    def __generate(
        self,
        pipe: StableDiffusionPipeline | StableDiffusionXLPipeline,
        prompt: str,
        negative_prompt: str,
    ):
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            generator=torch.Generator(device=self._device).manual_seed(
                self._model_config["manual_seed"]
            ),
            **self._model_config[self._model_name]["inference_opt"],
        ).images[0]
        return image

    def _generate_and_refine_image(
        self,
        pipe: StableDiffusionPipeline | StableDiffusionXLPipeline,
        prompt: str,
        negative_prompt: str,
        refine_img: bool = False,
    ) -> PIL:
        image = self.__generate(pipe, prompt, negative_prompt)

        if refine_img:
            refiner = self._get_refiner(pipe)
            image = self.__refine(refiner, image, prompt)

        gc.collect()
        torch.cuda.empty_cache()
        return image

    def save_images(
        self, image: PIL, prompt: str, negative_prompt: str, save_path
    ) -> None:
        # for Decoding: from PIL import Image; foo = Image.open(BytesIO(base64.b64decode(image_b64.split(",")[-1])))
        # save the image string encoded by base64
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_b64 = f"data:image/jpeg;{prompt};{negative_prompt};base64,{img_str}"
        with open(save_path + f"/texts/image_b64_{timestamp}.txt", "w") as text_file:
            text_file.write(image_b64)

        # save the image as PNG with unique timestamp
        filename = save_path + f"/pixels/image_{timestamp}.png"
        image.save(filename, format="PNG")

    def generate_images(
        self,
        prompt: str,
        negative_prompt: str,
        pipe: Optional[StableDiffusionXLPipeline] = None,
        save_path: str = "./imgs",
    ) -> PIL:
        if pipe is None:
            pipe = self.get_pipe(use_lora_weights=False)

        image = self._generate_and_refine_image(pipe, prompt, negative_prompt)
        self.save_images(image, prompt, negative_prompt, save_path=save_path)
        return image


def draw_your_mind(prompt: str) -> None:
    negative_prompt = "<your negative prompts>"

    draw = Drawing(model_name="sdxl-hello-world", model_config=MODEL_CONFIG)
    image = draw.generate_images(prompt=prompt, negative_prompt=negative_prompt)

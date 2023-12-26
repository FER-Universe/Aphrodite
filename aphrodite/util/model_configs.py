MODEL_CONFIG = {
    "pipe_opt": {
        "torch.dtype": "torch.float16",
        "variant": "fp16",
        "device": "cpu",
    },
    "inference_opt": {
        "num_inference_steps": 25,
        "guidance_scale": 7.0,
    },
    "sdxl-realistic": {
        "type": "name",
        "name": "",
    },
}

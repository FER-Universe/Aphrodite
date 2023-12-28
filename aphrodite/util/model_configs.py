MODEL_CONFIG = {
    # default configs
    "device": "cpu",  # cuda | mps | etc.
    "max_token_length": 77,
    "clip_skip": 2,  # or 1
    "manual_seed": 1234,
    # model configs
    "sdxl-hello-world": {
        "type": "name",
        "name": "/path/to/XXX.safetensors",
        "pipe_opt": {
            "torch.dtype": "torch.float16",
            "variant": "fp16",
            "device": "cpu",
            "safety_checker": None,
        },
        "inference_opt": {"num_inference_steps": 25, "guidance_scale": 7.0},
        "lora_path": "/path/to/XXX.safetensors",
    },
}

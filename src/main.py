from fastapi import FastAPI
from src.api.generate import router as generate_router 
import yaml
from src.core.build_patches import build_patch_manager  
from src.core.request_logging import RequestLoggingMiddleware
from src.core.logging_config import get_logger

CONFIG_PATH = "configs/config.yaml"
PATCHES_CONFIG_PATH = "configs/patches_config.yaml"

app = FastAPI(title="Self-Healing LLM Security Pipline")
app.include_router(generate_router)
app.add_middleware(RequestLoggingMiddleware)
logger = get_logger()   

@app.on_event("startup")
def _startup():
    with open(PATCHES_CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    pm = build_patch_manager(cfg)
    app.state.patch_manager = pm

    logger.info(
        "patch_manager_initialized",
        extra={
            "prompt_patches": [p.name for p in pm.prompt_patches],
            "output_patches": [p.name for p in pm.output_patches],
        },
    )


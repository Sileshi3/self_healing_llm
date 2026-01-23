from fastapi import FastAPI
from src.api.generate import router as generate_router
import yaml
from pathlib import Path
from src.core.build_patches import build_patch_manager
from src.core.request_logging import RequestLoggingMiddleware  
from src.core.config import get_logger, load_config

# Use absolute paths based on project root
BASE_DIR = Path(__file__).resolve().parent.parent
PATCHES_CONFIG_PATH = BASE_DIR / "configs" / "patches_config.yaml"
ABLATION_CONF = BASE_DIR / "configs" / "week4" / "patches_ablation_setting.yaml"

app = FastAPI(title="Self-Healing LLM Security Pipeline")       
app.include_router(generate_router)
app.add_middleware(RequestLoggingMiddleware)
logger = get_logger()

@app.on_event("startup")
def _startup():
    cfg = load_config(PATCHES_CONFIG_PATH)
    ablation_cfg = load_config(ABLATION_CONF) 

    pm = build_patch_manager(cfg, ablation_cfg)
    app.state.patch_manager = pm

    logger.info(
        "patch_manager_initialized",
        extra={
            "prompt_patches": [p.name for p in pm.prompt_patches],
            "output_patches": [p.name for p in pm.output_patches],
        },
    )
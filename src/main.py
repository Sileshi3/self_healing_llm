from fastapi import FastAPI
from src.api.generate import router as generate_router 
import yaml
from src.core.build_patches import build_patch_manager  

CONFIG_PATH = "configs/config.yaml"
PATCHES_CONFIG_PATH = "configs/patches_config.yaml"

app = FastAPI(title="Self-Healing LLM Security Pipline")
app.include_router(generate_router)

@app.on_event("startup")
def _startup():
    with open(PATCHES_CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    app.state.patch_manager = build_patch_manager(cfg)

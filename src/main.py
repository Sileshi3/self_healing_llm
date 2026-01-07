# from fastapi import FastAPI
# from src.api.generate import router as generate_router

# app = FastAPI(title="Self-Healing LLM Security Pipline")
# app.include_router(generate_router)






# from fastapi import FastAPI
# import yaml

# from src.api.generate import router as generate_router
# from src.core.build_patches import build_patch_manager

# app = FastAPI(title="Self-Healing LLM Security Pipline")
# app.include_router(generate_router)

# @app.on_event("startup")
# def startup():
#     with open("configs/config.yaml", "r") as f:
#         cfg = yaml.safe_load(f)
#     app.state.patch_manager = build_patch_manager(cfg)

# main.py
from fastapi import FastAPI
from src.api.generate import router as generate_router
import yaml
from src.core.build_patches import build_patch_manager  # wherever you put it

CONFIG_PATH = "configs/config.yaml"

app = FastAPI(title="Self-Healing LLM Security Pipline")
app.include_router(generate_router)

@app.on_event("startup")
def _startup():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    app.state.patch_manager = build_patch_manager(cfg)

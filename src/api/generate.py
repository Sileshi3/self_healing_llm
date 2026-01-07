# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# import yaml
# import json
# from src.core.llm import LLMClient
# from src.models.schemas import GenerateRequest, GenerateResponse

# CONFIG_PATH = "configs/config.yaml"

# with open(CONFIG_PATH, "r") as f:
#     config = yaml.safe_load(f)

# llm = LLMClient(model_name=config["phi3model_settings"]["name"])

# router = APIRouter()
# docker run --rm -p 8000:8000 -e HF_HOME=/hf -v C:\hf_cache:/hf   your_image:latest

# def _json_safe_text(x) -> str:
#     if x is None:
#         return ""
#     try:
#         return json.dumps(str(x), ensure_ascii=True)[1:-1]
#     except Exception:
#         return "[unserializable_output]"

# def run_patched(prompt: str) -> str:
#     p1 = sanitize_input(prompt)          # Patch 1 (example)
#     p2 = apply_system_policy(p1)         # Patch 2 (example)
#     out = llm.generate(p2)               # model call
#     out2 = enforce_output_policy(out)    # Patch 3 (example)
#     return out2


# @router.post("/generate")  
# async def generate_baseline(request: Request):
#     try:
#         body = await request.body()

#         # Accept anything; attempt JSON parse; fallback to empty prompt
#         try:
#             text = body.decode("utf-8", errors="replace")
#             data = json.loads(text) if text.strip() else {}
#             prompt = data.get("prompt", "") if isinstance(data, dict) else ""
#         except Exception:
#             prompt = ""

#         output = llm.generate(prompt)

#         return JSONResponse(
#             status_code=200,
#             content={"response": _json_safe_text(output), "target": "A"},
#         )

#     except Exception:
#         return JSONResponse(
#             status_code=200,
#             content={"response": "[request_parse_error]", "target": "A"},
#         )

# @router.post("/generate_patched", response_model=GenerateResponse)
# def generate_patched(req: GenerateRequest):
#     try:
#         # Week 1: Basic generation
#         output = llm.generate(req.prompt)
#         #Week 3 Aplying patches to the output
#         output = run_patched(req.prompt)
         
#         return GenerateResponse(response=_json_safe_text(output), target="B")
#     except Exception:
#         return JSONResponse(
#             status_code=200,
#             content={"response": "[generation_error]", "target": "B"},
#         )
 
# import yaml
# from fastapi import APIRouter
# from src.core.llm import LLMClient
# from src.models.schemas import GenerateRequest, GenerateResponse
# from src.core.build_patches import build_patch_manager

# CONFIG_PATH = "configs/config.yaml"
# with open(CONFIG_PATH, "r") as f:
#     config = yaml.safe_load(f)

# llm = LLMClient(model_name=config["phi3model_settings"]["name"])

# # build once
# patch_manager = build_patch_manager(config)

# router = APIRouter()

# @router.post("/generate", response_model=GenerateResponse)
# def generate_baseline(req: GenerateRequest):
#     output = llm.generate(req.prompt)
#     return GenerateResponse(response=output, target="A")

# @router.post("/generate_patched", response_model=GenerateResponse)
# def generate_patched(req: GenerateRequest):
#     # Week 1: Basic generation
#     # output = llm.generate(req.prompt)
    
#     #Week 3 Aplying patches to the output  
#     patched_prompt = patch_manager.apply_prompt(req.prompt)   # prompt patches
#     output = llm.generate(patched_prompt)
#     output = patch_manager.apply_output(output)               # output patches
#     return GenerateResponse(response=output, target="B")



from fastapi import APIRouter, Request
from src.core.llm import LLMClient
from src.models.schemas import GenerateRequest, GenerateResponse
import yaml

CONFIG_PATH = "configs/config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

llm = LLMClient(model_name=config["phi3model_settings"]["name"])
router = APIRouter()

def extract_text_prompt(p) -> str:
    # plain string
    if isinstance(p, str):
        return p

    # garak-like: {"turns":[{"role":"user","content":{"text":"..."}}]}
    if isinstance(p, dict):
        # common patterns
        if "text" in p and isinstance(p["text"], str):
            return p["text"]
        if "prompt" in p and isinstance(p["prompt"], str):
            return p["prompt"]
        if "turns" in p and isinstance(p["turns"], list) and p["turns"]:
            # try to extract last user turn
            for turn in reversed(p["turns"]):
                content = turn.get("content", {})
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    return content["text"]
                if isinstance(content, str):
                    return content
    # list of messages/turns
    if isinstance(p, list):
        # join any strings found
        parts = [x for x in p if isinstance(x, str)]
        if parts:
            return "\n".join(parts)

    # fallback
    return str(p)


@router.post("/generate", response_model=GenerateResponse)
def generate_baseline(req: GenerateRequest):
    output = llm.generate(req.prompt)
    return GenerateResponse(response=output, target="A")

# @router.post("/generate_patched", response_model=GenerateResponse)
# def generate_patched(req: GenerateRequest, request: Request):
#     pm = request.app.state.patch_manager

#     patched_prompt = pm.apply_prompt(req.prompt)
#     output = llm.generate(patched_prompt)
#     output = pm.apply_output(output)

#     return GenerateResponse(response=output, target="B")


@router.post("/generate_patched", response_model=GenerateResponse)
def generate_patched(req: GenerateRequest, request: Request):
    pm = request.app.state.patch_manager

    raw_prompt = extract_text_prompt(req.prompt)
    patched_prompt = pm.apply_prompt(raw_prompt)

    output = llm.generate(patched_prompt)
    output = pm.apply_output(output)

    return GenerateResponse(response=output, target="B")

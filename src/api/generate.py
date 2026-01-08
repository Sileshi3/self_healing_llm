
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
    raw_prompt = extract_text_prompt(req.prompt)
    output = llm.generate(raw_prompt)
    return GenerateResponse(response=output, target="A")


@router.post("/generate_patched", response_model=GenerateResponse)
def generate_patched(req: GenerateRequest, request: Request):
    pm = request.app.state.patch_manager
    
    raw_prompt = extract_text_prompt(req.prompt)
    patched_prompt = pm.apply_prompt(raw_prompt)

    output = llm.generate(patched_prompt) 
    try:
        output = pm.apply_output(output, patched_prompt)
    except TypeError:
        output = pm.apply_output(output)

    return GenerateResponse(response=f"[B_PATCHED]\n{output}", target="B")

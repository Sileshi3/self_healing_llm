
from fastapi import APIRouter, Request
from src.core.llm import LLMClient
from src.models.schemas import GenerateRequest, GenerateResponse
import yaml
from src.core.logging_config import get_logger 

logger = get_logger()   
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
def generate_baseline(req: GenerateRequest, request: Request):
    request_id = getattr(request.state, "request_id", None)
    raw_prompt = extract_text_prompt(req.prompt)
    logger.info("generate_A_called", extra={"request_id": request_id, "prompt_len": len(raw_prompt)})

    output = llm.generate(raw_prompt)
    return GenerateResponse(response=output, target="A")


@router.post("/generate_patched", response_model=GenerateResponse)
def generate_patched(req: GenerateRequest, request: Request):
    request_id = getattr(request.state, "request_id", None)

    pm = request.app.state.patch_manager
    
    raw_prompt = extract_text_prompt(req.prompt)
    logger.info("generate_B_called", extra={"request_id": request_id, "prompt_len": len(raw_prompt)})

    patched_prompt, prompt_logs = pm.apply_prompt_with_logs(raw_prompt, request_id=request_id)

    output = llm.generate(patched_prompt)  
    safe_output, out_logs = pm.apply_output_with_logs(patched_prompt, output, request_id=request_id)
    
    logger.info(
        "patch_manager_initialized",
        extra={
            "prompt_patches": [getattr(p, "name", p.__class__.__name__) for p in pm.prompt_patches],
            "output_patches": [getattr(p, "name", p.__class__.__name__) for p in pm.output_patches],
        },
    )
    # logger.info("generate_B_completed", extra={
    #     "request_id": request_id,
    #     "original_prompt_len": len(raw_prompt),
    #     "patched_prompt_len": len(patched_prompt),
    #     "original_output_len": len(output) if isinstance(output, str) else None,
    #     "safe_output_len": len(safe_output) if isinstance(safe_output, str) else None,
    #     "prompt_patches": [log.__dict__ for log in prompt_logs],
    #     "output_patches": [log.__dict__ for log in out_logs],
    # })
    return GenerateResponse(response=safe_output, target="B")




# This file defines the API endpoints for generating responses using the LLM, 
# both with and without patches. 
# It includes the logic for extracting text prompts from various input formats,
#  applying the patch manager,

from pdb import pm
from fastapi import APIRouter, Request
from src.core.llm import LLMClient
from src.models.schemas import GenerateRequest, GenerateResponse
import yaml
from src.core.config import get_logger 
from dataclasses import asdict  


logger = get_logger()   
CONFIG_PATH = "configs/main_config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

llm_config = config["llm_model_settings"]
llm = LLMClient(
    model_name=llm_config["name"],
    max_new_tokens=llm_config.get("max_new_tokens"),
    temperature=llm_config.get("temperature")
)
router = APIRouter()

def extract_text_prompt(p) -> str:
    # plain string
    if isinstance(p, str):
        return p
 
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
    
    # DEBUG: Check if patches are loaded
    print(f"DEBUG: prompt_patches = {[p.name for p in pm.prompt_patches]}")
    print(f"DEBUG: output_patches = {[p.name for p in pm.output_patches]}")

    raw_prompt = extract_text_prompt(req.prompt)
    
    logger.info("generate_B_called", 
                extra={"request_id": request_id, 
                       "prompt_len": len(raw_prompt)})
 
    patched_prompt, in_logs = pm.apply_prompt_with_logs(req.prompt, request_id=request_id)
    raw_output = llm.generate(patched_prompt)
    
    print("DEBUG original len:", len(req.prompt)) 
    print("DEBUG patched len:", len(patched_prompt))

    safe_output, out_logs = pm.apply_output_with_logs(
        prompt=patched_prompt,   
        output=raw_output,
        request_id=request_id
    )
    logger.info("Safe output generated", extra={"request_id": request_id, 
                                                "raw_prompt": raw_prompt,
                                                  "output": (raw_output)})
    return {
    "response": safe_output,
    "target": "B",               
    "request_id": request_id,
    "prompt_patches": [asdict(l) for l in in_logs],
    "output_patches": [asdict(l) for l in out_logs],
    }

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import yaml
import json
from src.core.llm import LLMClient
from src.models.schemas import GenerateRequest, GenerateResponse

CONFIG_PATH = "configs/config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

llm = LLMClient(model_name=config["phi3model_settings"]["name"])

router = APIRouter()

def _json_safe_text(x) -> str:
    if x is None:
        return ""
    try:
        return json.dumps(str(x), ensure_ascii=True)[1:-1]
    except Exception:
        return "[unserializable_output]"

@router.post("/generate")  
async def generate_baseline(request: Request):
    try:
        body = await request.body()

        # Accept anything; attempt JSON parse; fallback to empty prompt
        try:
            text = body.decode("utf-8", errors="replace")
            data = json.loads(text) if text.strip() else {}
            prompt = data.get("prompt", "") if isinstance(data, dict) else ""
        except Exception:
            prompt = ""

        output = llm.generate(prompt)

        return JSONResponse(
            status_code=200,
            content={"response": _json_safe_text(output), "target": "A"},
        )

    except Exception:
        return JSONResponse(
            status_code=200,
            content={"response": "[request_parse_error]", "target": "A"},
        )

@router.post("/generate_patched", response_model=GenerateResponse)
def generate_patched(req: GenerateRequest):
    try:
        output = llm.generate(req.prompt)
        return GenerateResponse(response=_json_safe_text(output), target="B")
    except Exception:
        return JSONResponse(
            status_code=200,
            content={"response": "[generation_error]", "target": "B"},
        )

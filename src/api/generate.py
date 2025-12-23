import yaml
# import os
from fastapi import APIRouter
from src.core.llm import LLMClient
from src.models.schemas import GenerateRequest, GenerateResponse

CONFIG_PATH = "configs/config.yaml"

# Read configuration from config file
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Print the type in Docker logs for debug
print(f"DEBUG: Config type is {type(config)}")

# Accessing the dictionary for model setting from config file 
llm = LLMClient(model_name=config["phi3model_settings"]["name"])
#llm = LLMClient(model_name=config["model_settings"]["name"])


router = APIRouter()


# logic for Target A (baseline)
@router.post("/generate", response_model=GenerateResponse)
def generate_baseline(req: GenerateRequest):
    output = llm.generate(req.prompt)
    return GenerateResponse(response=output, target="A")


# logic for Target B (patched gateway)
@router.post("/generate_patched", response_model=GenerateResponse)
def generate_patched(req: GenerateRequest):
    output = llm.generate(req.prompt)
    return GenerateResponse(response=output, target="B")

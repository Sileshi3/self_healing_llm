from fastapi import APIRouter
from src.core.llm import LLMClient
from src.models.schemas import GenerateRequest, GenerateResponse

router=APIRouter()
llm=LLMClient(model_name="baseline_model")

#logic for Target A (baseline)
@router.post("/generate",response_model=GenerateResponse)
def generate_baseline(req:GenerateRequest):
    output=llm.generate(req.prompt)
    return  GenerateResponse(response=output,target="A")

#logic for Target B (patched gateway)
@router.post("/generate_patched",response_model=GenerateResponse)
def generate_patched(req:GenerateRequest):
    output=llm.generate(req.prompt)
    return  GenerateResponse(response=output,target="B")
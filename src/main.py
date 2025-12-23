from fastapi import FastAPI
from src.api.generate import router as generate_router

app = FastAPI(title="Self-Healing LLM Security Pipline")
app.include_router(generate_router)

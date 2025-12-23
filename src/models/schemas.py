from pydantic import BaseModel

# A request generator class
class GenerateRequest(BaseModel):
    prompt: str


# A response generator class
class GenerateResponse(BaseModel):
    response: str
    target: str

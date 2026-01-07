from pydantic import BaseModel
from typing import Any, Optional, Union, List, Dict

# A request generator class
class GenerateRequest(BaseModel):
    prompt: Union[str, Dict[str, Any], List[Any]]


# A response generator class
class GenerateResponse(BaseModel):
    response: str
    target: str

 
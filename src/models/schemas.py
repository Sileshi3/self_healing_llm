from pydantic import BaseModel
from typing import Any, Optional, Union, List, Dict
# This file defines the data models for the API requests and responses, as well as any other shared data structures.
# A request generator class
class GenerateRequest(BaseModel):
    prompt: Union[str, Dict[str, Any], List[Any]]


# A response generator class
class GenerateResponse(BaseModel):
    response: str
    target: str

 
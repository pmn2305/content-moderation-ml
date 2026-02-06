from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict


class ModerateRequest(BaseModel):
    text: str|None


class ModerateResponse(BaseModel):
    decision: str
    scores: Dict[str, float]
    model_versions: Dict[str, str]

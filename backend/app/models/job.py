from pydantic import BaseModel
from typing import Optional

class JobResult(BaseModel):
    title: str
    location: Optional[str]
    company: Optional[str]
    url: Optional[str] = None  # We'll populate this later if the API adds it
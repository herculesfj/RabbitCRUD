from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    value: Optional[int] = None

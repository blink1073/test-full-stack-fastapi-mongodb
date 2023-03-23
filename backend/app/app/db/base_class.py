from typing import Any

from pydantic import BaseModel



class Base(BaseModel):
    id: Any
    __name__: str

from typing import Any

from pydantic import BaseModel



class Base(BaseModel):
    id: Any
    __name__: str

    @classmethod
    def column_name(cls) -> str:
        return cls.__name__.lower() + 's'

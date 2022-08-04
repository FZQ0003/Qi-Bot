from typing import Any

from pydantic import BaseModel, Field, validator


class QiModel(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    @validator('*', pre=True)
    def __default(cls, v: Any, field: Field) -> Any:
        if v is None:
            return getattr(field, 'default', None)
        return v

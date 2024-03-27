"""Qi-Bot base model."""
from pydantic import BaseModel


class QiModel(BaseModel):
    """Qi-Bot base model."""

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    # Auto-detecting arguments is broken. You should implement __init__() method yourself.
    # def __init__(self, /, _frozen: bool = False, **data):
    #     super().__init__(**data)
    #     self.model_config['frozen'] = _frozen  # noqa

    # Note: Use Undefined to parse fields that need default values instead of None.
    # noinspection PyNestedDecorators
    # @field_validator('*', mode='before')
    # @classmethod
    # def __default(cls, data: Any, v_info: ValidationInfo) -> Any:
    #     if data is None:
    #         if f_info := cls.model_fields.get(v_info.field_name, None):  # noqa
    #             if isinstance(f_info.default, f_info.annotation):
    #                 return f_info.default
    #     return data

"""Qi-Bot base model."""
from types import UnionType

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


class LateInitObject:
    """Custom object that can auto-init attributes."""
    _auto_init: bool = True
    _error_no_attr: bool = False

    def __init__(self, auto_init: bool = True, error_no_attr: bool = False):
        self._auto_init = auto_init
        self._error_no_attr = error_no_attr

    def __getattr__(self, item):
        if self._auto_init:
            # Create attribute if there is an annotation
            type_attr: type | str = self.__annotations__.get(item, '')
            if isinstance(type_attr, UnionType):
                type_attr = type_attr.__args__[0]
            if isinstance(type_attr, type):
                init_value = type_attr()
                super().__setattr__(item, init_value)
                return init_value
        if self._error_no_attr:
            # Same as object
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")
        return None

    def __setattr__(self, key, value):
        # Check type if there is an annotation
        type_attr: type | str = self.__annotations__.get(key, '')
        if isinstance(type_attr, type):
            type_attr_list = type_attr.__args__ if isinstance(type_attr, UnionType) else [type_attr]
            type_value = type(value)
            error_types = type_value.__name__, [_.__name__ for _ in type_attr_list]
        elif isinstance(type_attr, str) and type_attr:
            type_attr_list = type_attr.replace(' ', '').split('|')
            type_value = type(value).__name__
            error_types = type_value, type_attr_list
        elif self._error_no_attr:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
        else:
            # Same as object
            return super().__setattr__(key, value)
        if type_value in type_attr_list:
            return super().__setattr__(key, value)
        raise AttributeError(f"Input type '{error_types[0]}' does not match "
                             f"attribute type(s) [{error_types[1]}]")

"""Qi-Bot stored data during runtime."""
from types import UnionType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config.bot import BotConfigModel


class LateInitObject:

    def __getattr__(self, item):
        # Create attribute if there is an annotation
        type_attr: type | str = self.__annotations__.get(item, '')
        if isinstance(type_attr, UnionType):
            type_attr = type_attr.__args__[0]
        if isinstance(type_attr, type):
            init_value = type_attr()
            super().__setattr__(item, init_value)
            return init_value
        # Same as object
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        # TODO: UnionType & type & str
        # Check type if there is an annotation
        type_attr: type | str = self.__annotations__.get(key, '')
        # if isinstance(type_attr, UnionType):
        #     type_attr = type_attr.__args__[0]
        if isinstance(type_attr, type) and type(value) is not type_attr:
            raise AttributeError(f"Input type '{type(value).__name__}' does not match "
                                 f"attribute type '{self.__annotations__[key].__name__}'")
        # if isinstance(type_attr, str) and type(value) != type_attr:
        #     raise AttributeError(f"Input type '{type(value).__name__}' does not match "
        #                          f"attribute type '{self.__annotations__[key].__name__}'")
        # Same as object
        super().__setattr__(key, value)


class CurrentDataObject(LateInitObject):
    bot_config: 'BotConfigModel'


current = CurrentDataObject()

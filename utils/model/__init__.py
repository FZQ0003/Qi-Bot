"""Qi-Bot model manager."""
from .model import QiModel, LateInitObject

from pydantic import (
    Field, ConfigDict,  # noqa: F401
    AliasChoices,  # noqa: F401
    field_validator, model_validator,  # noqa: F401
    ValidationError)  # noqa: F401
from pydantic_core import PydanticUndefined as Undefined  # noqa: F401

# Legacy validator method for compatibility
validator = field_validator

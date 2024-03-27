"""Qi-Bot model manager."""
from .model import QiModel

from pydantic import (
    Field, ConfigDict,
    AliasChoices,
    field_validator, model_validator,
    ValidationError)
from pydantic_core import PydanticUndefined as Undefined

# Legacy validator method for compatibility
validator = field_validator

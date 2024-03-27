"""File config models."""
from ..model import QiModel, Field


class CacheConfigModel(QiModel):
    """Model for cache config."""
    enable: bool = True
    max_count: int = Field(-1, ge=-1)
    expire_days: int = Field(30, ge=0)


class FileConfigModel(QiModel):
    """Model for file config."""
    cache: CacheConfigModel = CacheConfigModel()

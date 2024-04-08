"""Crypto related config models."""
import hashlib

from ..logger import logger
from ..model import QiModel, field_validator


class HashConfigModel(QiModel):
    """Model for hash related config."""
    algorithm: str = 'sha3_512'

    # noinspection PyNestedDecorators
    @field_validator('algorithm')
    @classmethod
    def __check_algorithm(cls, data: str) -> str:
        if data not in hashlib.algorithms_available:
            logger.warning(f'{data} not available, use sha3_512 instead.')
            data = 'sha3_512'
        return data


class HmacConfigModel(QiModel):
    """Model for hmac config."""
    key: bytes = b''
    save_key: bool = False

    # noinspection PyNestedDecorators
    @field_validator('key', mode='before')
    @classmethod
    def __parse_key(cls, data: bytes | str) -> bytes:
        if isinstance(data, str):
            return data.encode()
        return data


class CryptoConfigModel(QiModel):
    """Model for crypto related config."""
    hash: HashConfigModel = HashConfigModel()
    hmac: HmacConfigModel = HmacConfigModel()

"""Crypto related config models."""
import hashlib
import platform

from ..file import Data
from ..model import QiModel, field_validator, model_validator


class HashConfigModel(QiModel):
    """Model for hash related config."""
    algorithm: str = 'sha3_512'

    # noinspection PyNestedDecorators
    @field_validator('algorithm')
    @classmethod
    def __check_algorithm(cls, data: str) -> str:
        if data not in hashlib.algorithms_available:
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

    @model_validator(mode='after')
    def __generate_hmac_key(self) -> 'CryptoConfigModel':
        if not self.hmac.key:
            self.hmac.key = Data(
                filename='hash_key', suffix='bin', is_bin=True
            ).executor(
                read=self.hmac.save_key, write=self.hmac.save_key
            )(
                lambda header: hashlib.new(
                    self.hash.algorithm,
                    f'{header}, {platform.node()}, {platform.processor()}'.encode()
                ).digest()
            )('Qi-Bot')
        return self

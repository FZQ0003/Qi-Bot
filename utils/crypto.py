import hashlib
import hmac

from .config import bot_config


def hash_new(data: bytes | str = b''):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.new(bot_config.crypto.hash.algorithm, data)


def hmac_new(data: bytes | str = b''):
    if isinstance(data, str):
        data = data.encode()
    return hmac.new(bot_config.crypto.hmac.key, data, bot_config.crypto.hash.algorithm)


def hash_encode(data: bytes | str, return_hex: bool = True) -> bytes | str:
    output = hash_new(data)
    return output.hexdigest() if return_hex else output.digest()


def hmac_encode(data: bytes | str, return_hex: bool = True) -> bytes | str:
    output = hmac_new(data)
    return output.hexdigest() if return_hex else output.digest()

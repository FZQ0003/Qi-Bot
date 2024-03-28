import hashlib
import hmac

from .config import bot_config


def hash_encode(data: bytes | str, return_hex: bool = True) -> bytes | str:
    if isinstance(data, str):
        data = data.encode()
    output = hashlib.new(bot_config.crypto.hash.algorithm, data)
    return output.hexdigest() if return_hex else output.digest()


def hmac_encode(data: bytes | str, return_hex: bool = True) -> bytes | str:
    if isinstance(data, str):
        data = data.encode()
    output = hmac.new(bot_config.crypto.hmac.key, data, bot_config.crypto.hash.algorithm)
    return output.hexdigest() if return_hex else output.digest()

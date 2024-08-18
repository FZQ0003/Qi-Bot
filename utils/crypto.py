"""Qi-Bot crypto related utilities."""
import hashlib
import hmac

from .stored_data import current


def hash_new(data: bytes | str = b''):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.new(current.bot_config.crypto.hash.algorithm, data)


def hmac_new(data: bytes | str = b''):
    if isinstance(data, str):
        data = data.encode()
    return hmac.new(current.bot_config.crypto.hmac.key, data, current.bot_config.crypto.hash.algorithm)


def hash_encode(data: bytes | str, return_hex: bool = True) -> bytes | str:
    output = hash_new(data)
    return output.hexdigest() if return_hex else output.digest()


def hmac_encode(data: bytes | str, return_hex: bool = True) -> bytes | str:
    output = hmac_new(data)
    return output.hexdigest() if return_hex else output.digest()

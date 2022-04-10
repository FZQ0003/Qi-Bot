from hashlib import md5
from typing import Union


def hash_encode(data: Union[str, bytes],
                return_bytes: bool = False) -> Union[str, bytes]:
    if isinstance(data, str):
        data = data.encode()
    output = md5(data)
    return output.digest() if return_bytes else output.hexdigest()

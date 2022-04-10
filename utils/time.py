from time import time


def get_int_time() -> int:
    return int(time())


def get_str_time(ms: bool = False) -> str:
    output = str(time()).split('.')
    if ms:
        return '-'.join(output)
    return output[0]

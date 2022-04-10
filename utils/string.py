import re


def to_camel(string: str, is_big: bool = False) -> str:
    """下划线转驼峰"""
    if is_big:
        string = '_' + string
    return re.sub(r'(_[a-z])', lambda x: x.group()[1].upper(), string)


def to_snake(string: str) -> str:
    """驼峰转下划线"""
    if '_' in string:
        raise ValueError(f'Cannot convert {string}')
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', string).lower()

import re


def snake_to_camel(string: str, upper: bool = False) -> str:
    """'foo_bar' -> 'fooBar' (upper=False) / 'FooBar' (upper=True)."""
    if upper:
        string = '_' + string
    return re.sub(r'(_[a-z])', lambda x: x.group()[1].upper(), string)


def camel_to_snake(string: str) -> str:
    """'fooBar' / 'FooBar' -> 'foo_bar'."""
    # if '_' in string:
    #     raise ValueError(f'Cannot convert {string}')
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', string).lower()


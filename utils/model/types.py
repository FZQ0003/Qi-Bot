"""Useful annotated types."""
from typing import Annotated

import annotated_types
from pydantic import Field, HttpUrl, UrlConstraints
from pydantic_core import Url

# Integers
IDAccount = Annotated[int, annotated_types.Ge(0)]
QQAccount = Annotated[int, annotated_types.Ge(10000), annotated_types.Le(9999999999)]
Port = Annotated[int, annotated_types.Ge(1), annotated_types.Le(65535)]
Filemode = Annotated[int, annotated_types.Ge(0), annotated_types.Le(0o777)]

# Patterns
# __pattern_host = r'(xn--[a-zA-Z\d]+|[+\w~]+)(.(xn--[a-zA-Z\d]+|[+\w~]+))*'

# Strings
Module = Annotated[str, Field(pattern=r'^\w+(\.\w+)*$')]
Host = Annotated[str, Field(pattern=r'^(xn--[a-zA-Z\d]+|[+\w~]+)(.(xn--[a-zA-Z\d]+|[+\w~]+))*$')]
# MiraiURL = Annotated[str, Field(pattern=r'^((http|ws)://)?' + __pattern_host + r'(:\d+)?/?$')]
Filename = Annotated[str, Field(pattern=r'^[-.\w /]{1,200}$')]

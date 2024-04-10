"""Cache file manager."""
from typing import Callable, Sequence, TypeVar, ParamSpec

from . import DataFile
from ..config import bot_config
from ..crypto import hmac_new
from ..model import model_validator, field_validator
from ..model.types import Filename

T = TypeVar('T')
P = ParamSpec('P')
ConfigValue = ...

__all__ = [
    'CacheFile',
    'Cache'
]


class CacheFile(DataFile):
    """Cache file manager.

    Attributes:
        filename (str): This can be ignored.
        enable (bool): Manually enable cache.
        no_name (bool): If set, The filename will be generated automatically.
        header (bytes): For generating filename.
        read_args (Sequence[int | str]): For generating filename.

    Notes:
        Use header + (args or kwargs)[read_args[i]] as HMAC input.

        The "read_args" attribute MUST be correctly set. For example::

            @Cachefile(no_name=True, header=b'Header', read_args=['arg_2', 1])
            def function(arg_0: int, arg_1: str, arg_2: str, ...) -> ...:
                ...

            function(0, 'a', arg_2='b')  # important

        The result filename is ``hmac(global_key, header + kwargs['arg_2'] + args[1])``.

        You must ensure types of ``args[1]`` and ``kwargs['arg_2']`` are all str or bytes.
        In this example, it is recommended to set ``read_args=[2, 'arg_2', 1, 'arg_1']``
        and NOT to set default values to parse both arg_1 and arg_2. NOTE THE ORDER.

        Known issue: Type checking may not be passed. Use #noqa to avoid this.
    """
    filename: Filename = '.no-init'
    enable: bool = ConfigValue
    no_name: bool = False
    header: bytes = b''
    read_args: Sequence[int | str] = []

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def __init_enable_state(cls, data: dict[str, ...]) -> dict[str, ...]:
        if isinstance(data, dict) and data.get('enable', None) is None:
            data['enable'] = bot_config.file.cache.enable
        return data

    # noinspection PyNestedDecorators
    @field_validator('header', mode='before')
    @classmethod
    def __parse_header(cls, data: bytes | str) -> bytes:
        if isinstance(data, str):
            return data.encode()
        return data

    def _exec_pre(self, *args, **kwargs):
        # Generate filename
        if self.no_name:
            hmac = hmac_new(self.header)
            # See docstring.
            for arg_i in self.read_args:
                try:
                    if isinstance(arg_i, int) and isinstance((arg := args[arg_i]), (bytes, str)):
                        hmac.update(arg)
                    elif isinstance((arg := kwargs[arg_i]), (bytes, str)):
                        hmac.update(arg)
                except LookupError:
                    pass
            # The filename is never empty, but may be duplicated.
            self.filename = hmac.hexdigest()

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        return self.executor(self.enable, self.enable)(func)


class Cache(CacheFile):
    prefix: str = 'cache'

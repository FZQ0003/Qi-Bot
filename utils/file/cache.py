"""Cache file manager."""
from typing import Callable

from . import DataFile
from ..crypto import hmac_encode
from ..model import model_validator
from ..model.types import Filename
from ..string import connect_str_or_bytes


def _get_first_arg(items) -> str | bytes:
    for item in items:
        if isinstance(item, (str, bytes)):
            return item
    return ''


class CacheFile(DataFile):
    """Cache file manager.

    Attributes:
        filename (str): This can be ignored.
        enable (bool): Manually enable cache.
        no_name (bool): If set, The filename will be generated automatically.
        header (bytes | str): For generating filename.
        read_args (list[int | str]): For generating filename.

    Notes:
        Use header + (args or kwargs)[read_args[i]] as HMAC input.

        The "read_args" attribute MUST be correctly set. For example::

            @Cachefile(no_name=True, header='Header', read_args=['arg_2', 1])
            def function(arg_0: int, arg_1: str, arg_2: str, ...) -> ...:
                ...

            function(0, 'a', arg_2='b')  # important

        The result filename is ``hmac(global_key, header + kwargs['arg_2'] + args[1])``.

        You must ensure types of ``args[1]`` and ``kwargs['arg_2']`` are all str or bytes.
        In this example, it is recommended to set ``read_args=[2, 'arg_2', 1, 'arg_1']``
        and NOT to set default values to parse both arg_1 and arg_2. NOTE THE ORDER.
    """
    filename: Filename = '.no-init'
    enable: bool = True
    no_name: bool = False
    header: bytes | str = ''
    read_args: list[int | str] = []

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def __init_enable_state(cls, data: dict[str, ...]) -> dict[str, ...]:
        if isinstance(data, dict) and data.get('enable', None) is None:
            from ..config.bot import bot_config
            data['enable'] = bot_config.file.cache.enable
        return data

    def _exec_pre(self, *args, **kwargs):
        if self.no_name:
            tmp_msg_list = [self.header]
            for arg_i in self.read_args:
                try:
                    if isinstance(arg_i, int) and isinstance((arg := args[arg_i]), (bytes, str)):
                        tmp_msg_list.append(arg)
                    elif isinstance((arg := kwargs[arg_i]), (bytes, str)):
                        tmp_msg_list.append(arg)
                except LookupError:
                    pass
            self.filename = hmac_encode(
                connect_str_or_bytes(*tmp_msg_list, output_type=bytes),
                return_hex=True
            )
            # TODO: Warn or raise error if self.filename is empty.

    def __call__(self, func: Callable):
        return self.executor(self.enable, self.enable)(func)


class Cache(CacheFile):
    prefix: str = 'cache'

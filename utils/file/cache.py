"""TODO: Cache file manager."""
from typing import Callable

from . import DataFile, DataCheckError
from ..hash import hash_encode
from ..model import model_validator, ValidationError, Undefined
from ..model.types import Filename


def _get_first_arg(items) -> str | bytes:
    for item in items:
        if isinstance(item, (str, bytes)):
            return item
    return ''


class CacheFile(DataFile):
    filename: Filename = '.no-init'
    enable: bool = Undefined
    no_init: bool = False
    header: bytes = b''

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def __init_enable_state(cls, data: dict[str, ...]) -> dict[str, ...]:
        if isinstance(data, dict) and data.get('enable', None) is None:
            from ..config.bot import bot_config
            data['enable'] = bot_config.file.cache.enable
        return data

    @staticmethod
    def encode(content: str | bytes,
               header: str | bytes = None) -> str:
        if isinstance(content, str):
            content = content.encode()
        if header is not None:
            if isinstance(header, str):
                header = header.encode()
            content = header + content
        return hash_encode(content)

    @staticmethod
    def _exec_pre_encode(arg) -> bytes:
        # TODO: Encode?
        pass

    def _exec_pre(self, *args, **kwargs):
        ...
        # if self.no_init:
        #     # Read the first str/bytes arg for generating filename
        #     # Read cache flag (or the last arg) to enable cache
        #     input_arg = _get_first_arg(args)
        #     if not input_arg:
        #         input_arg = _get_first_arg(kwargs.values())
        #     if not input_arg:
        #         raise DataCheckError('Cannot specify filename!')
        #     self.filename = self.encode(input_arg, self.header)
        #     if isinstance(kwargs.get('cache', None), bool):
        #         self.enable = kwargs['cache']
        #     elif isinstance(args[-1], bool):
        #         self.enable = args[-1]
        #     else:
        #         self.enable = True

    def __call__(self, func: Callable):
        return self.executor(self.enable, self.enable)(func)


class Cache(CacheFile):
    prefix: str = 'cache'

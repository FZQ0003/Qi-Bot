from functools import wraps
from pathlib import Path
from typing import Any, Union, Callable, Optional

from .error import DataCheckError
from ..const import FILE
from ..hash import hash_encode
from ..model import QiModel, validator

CACHE_ENABLE = FILE.CACHE_ENABLE
NEWLINE = FILE.NEWLINE


def _get_first_arg(items) -> Union[str, bytes]:
    output = None
    for item in items:
        if isinstance(item, str) or isinstance(item, bytes):
            output = item
            break
    return output if output else ''


class CommonFile(QiModel):
    """
    Common File Manager
    Format: category/filename.suffix
    """
    filename: str
    category: Optional[str] = ''
    suffix: Optional[str] = ''
    is_elf: Optional[bool] = True

    def __init__(self,
                 filename: str,
                 category: str = None,
                 suffix: str = None,
                 is_elf: bool = None,
                 **kwargs):
        super().__init__(filename=filename,
                         category=category,
                         suffix=suffix,
                         is_elf=is_elf,
                         **kwargs)

    # noinspection PyMethodParameters
    @validator('filename')
    def __filename(cls, v: Any) -> Any:
        if not v:
            raise ValueError('Value is empty!')
        return v

    def __str__(self):
        return '<{} object: {} at {}>'.format(
            self.__class__.__name__,
            self.path,
            hex(id(self))
        )

    @property
    def path(self) -> Path:
        suffix = f'.{self.suffix}' if self.suffix else ''
        return Path(self.category, f'{self.filename}{suffix}')

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    def read(self) -> Any:
        if not self.exists:
            raise DataCheckError(f'{self.path} not found!')
        if self.is_elf:
            return self.path.read_bytes()
        else:
            text = self.path.read_text()
            if text.endswith('\n') and NEWLINE:
                return text[:-1]
            return text

    def write(self, data: Any) -> int:
        if not self.path.parent.is_dir():
            self.path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        if self.is_elf:
            return self.path.write_bytes(data)
        else:
            # Add a new line for text
            if NEWLINE:
                data += '\n'
            return self.path.write_text(data)

    def delete(self):
        self.path.unlink(True)


class DataFile(CommonFile):
    """
    Data File Manager
    Use @executor() to manage automatically
    """

    def _exec_pre(self, *args, **kwargs):
        pass

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def _exec_post(self, output, input_args: tuple, input_kwargs: dict):
        if not output:
            raise DataCheckError(f'No output!')
        return output

    def executor(self, read: bool = True, write: bool = True) -> Callable:
        def __func(func: Callable) -> Callable:
            @wraps(func)
            def __wrapper(*args, **kwargs) -> Any:
                # Pre-process function
                self._exec_pre(*args, **kwargs)
                # Read data, continue when failed
                # Note: No check if succeed
                if read:
                    try:
                        return self.read()
                    except DataCheckError:
                        pass
                # Execute function
                output = func(*args, **kwargs)
                # After-process function
                output = self._exec_post(output, args, kwargs)
                # Write data and return
                if write:
                    self.write(output)
                return output

            return __wrapper

        return __func


class Cache(DataFile):
    enable: Optional[bool] = CACHE_ENABLE
    no_init: Optional[bool] = False
    header: Optional[bytes] = None

    def __init__(self,
                 filename: str = None,
                 category: str = None,
                 suffix: str = None,
                 is_elf: bool = None,
                 enable: bool = None,
                 no_init: bool = False,
                 header: Union[str, bytes] = b''):
        if no_init:
            filename = '.no-init'
        if isinstance(header, str):
            header = header.encode()
        super().__init__(
            filename, category, suffix, is_elf,
            enable=enable, no_init=no_init, header=header
        )

    @staticmethod
    def encode(content: Union[str, bytes],
               header: Union[str, bytes] = None) -> str:
        if isinstance(content, str):
            content = content.encode()
        if header is not None:
            if isinstance(header, str):
                header = header.encode()
            content = header + content
        return hash_encode(content)

    @property
    def path(self) -> Path:
        return Path('cache', super().path)

    @staticmethod
    def _exe_pre_encode(arg: Any) -> bytes:
        # TODO: Encode?
        pass

    def _exec_pre(self, *args, **kwargs):
        if self.no_init:
            # Read the first str/bytes arg for generating filename
            # Read cache flag (or the last arg) to enable cache
            input_arg = _get_first_arg(args)
            if not input_arg:
                input_arg = _get_first_arg(kwargs.values())
            if not input_arg:
                raise DataCheckError('Cannot specify filename!')
            self.filename = self.encode(input_arg, self.header)
            if isinstance(kwargs.get('cache', None), bool):
                self.enable = kwargs['cache']
            elif isinstance(args[-1], bool):
                self.enable = args[-1]
            else:
                self.enable = True
            self.enable = self.enable and CACHE_ENABLE

    def __call__(self, func: Callable):
        return self.executor(self.enable, self.enable)(func)


class Data(DataFile):
    @property
    def path(self) -> Path:
        return Path('data', super().path)


class ConfigFile(CommonFile):
    """
    Config File Manager
    Use reader() and writer() to handle different types
    """
    is_elf: bool = False

    @staticmethod
    def reader(source: Any) -> dict:
        raise NotImplementedError

    @staticmethod
    def writer(config: dict) -> Any:
        raise NotImplementedError

    def read(self, target_model=None) -> Any:
        output = self.reader(super().read())
        if target_model is None:
            return output
        return target_model(**output)

    def write(self, data: Union[dict, object]) -> int:
        if isinstance(data, object):
            data = data.__dict__
        return super().write(self.writer(data))


# noinspection PyAbstractClass
class Config(ConfigFile):
    @property
    def path(self) -> Path:
        return Path('config', super().path)

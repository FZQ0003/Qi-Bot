from hashlib import md5 as hash_str
from pathlib import Path
from typing import Any, Union, Callable, Optional

from ..model import QiModel

CACHE_ENABLE = True


class CommonFile(QiModel):
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

    def __str__(self):
        return '<{} object: {} at {}>'.format(
            self.__class__.__name__,
            self.path_str,
            hex(id(self))
        )

    @property
    def path_str(self) -> str:
        if self.category == '':
            prefix = ''
        else:
            prefix = f'{self.category}/'
        if self.suffix == '':
            suffix = ''
        else:
            suffix = f'.{self.suffix}'
        return f'{prefix}{self.filename}{suffix}'

    @property
    def path(self) -> Path:
        return Path(self.path_str)

    def read(self) -> Any:
        if not self.exists:
            return None
        if self.is_elf:
            return self.path.read_bytes()
        else:
            return self.path.read_text()

    def write(self, data: Any) -> int:
        if not self.path.parent.is_dir():
            self.path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        if self.is_elf:
            return self.path.write_bytes(data)
        else:
            return self.path.write_text(data)

    def delete(self):
        self.path.unlink(True)

    @property
    def exists(self) -> bool:
        return self.path.is_file()


class Cache(CommonFile):
    enable: Optional[bool] = CACHE_ENABLE
    _no_init: bool = False
    _header: bytes = None

    def __init__(self,
                 filename: str,
                 category: str = None,
                 suffix: str = None,
                 is_elf: bool = None,
                 enable: bool = None):
        super().__init__(filename, category, suffix, is_elf, enable=enable)

    @staticmethod
    def encode(content: Union[str, bytes],
               header: Union[str, bytes] = None) -> str:
        if isinstance(content, str):
            content = content.encode('utf-8')
        if header is not None:
            if isinstance(header, str):
                header = header.encode('utf-8')
            content = header + content
        return hash_str(content).hexdigest()

    @classmethod
    def create(cls,
               content: Union[str, bytes],
               header: Union[str, bytes] = None,
               enable: bool = None):
        return cls(cls.encode(content, header), enable=enable)

    @classmethod
    def late_init(cls, header: Union[str, bytes] = None):
        output = cls('.no-init')
        output._no_init = True
        output._header = header
        return output

    @property
    def path_str(self) -> str:
        return 'cache/' + super().path_str

    @staticmethod
    def data_check(data: bytes) -> None:
        pass

    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            if self._no_init:
                # Read the first arg for generating filename
                # Read cache flag (or the last arg) to enable cache
                self.filename = self.encode(args[0], self._header)
                if isinstance(kwargs.get('cache', None), bool):
                    self.enable = kwargs['cache']
                elif isinstance(args[-1], bool):
                    self.enable = args[-1]
                else:
                    self.enable = CACHE_ENABLE
            if self.exists and self.enable:
                return self.read()
            output = func(*args, **kwargs)
            self.data_check(output)
            if self.enable:
                self.write(output)
            return output

        return wrapper


class Config(CommonFile):
    is_elf: bool = False

    def __init__(self,
                 filename: str,
                 category: str = None,
                 suffix: str = None):
        super().__init__(filename, category, suffix)

    @property
    def path_str(self) -> str:
        return 'config/' + super().path_str

    @staticmethod
    def _read_data(text: str) -> dict:
        raise NotImplementedError

    def read(self) -> dict:
        return self._read_data(super().read())

    @staticmethod
    def _write_data(data: dict) -> str:
        raise NotImplementedError

    def write(self, data: dict) -> int:
        return super().write(self._write_data(data))

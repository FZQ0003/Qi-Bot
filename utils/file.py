from hashlib import md5 as hash_str
from pathlib import Path
from typing import Any, Union, Callable

import pysilk

CACHE_ENABLE = True


# TODO: Use pydantic.
class CommonFile(object):
    filename: str
    category: str = ''
    suffix: str = ''
    is_elf: bool = True

    def __init__(self,
                 filename: str,
                 category: str = None,
                 suffix: str = None,
                 is_elf: bool = None):
        self.filename = filename
        if category is not None:
            self.category = category
        if suffix is not None:
            self.suffix = suffix
        if is_elf is not None:
            self.is_elf = is_elf

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
    enable: bool = CACHE_ENABLE
    no_init: bool = False

    def __init__(self,
                 filename: str,
                 category: str = None,
                 suffix: str = None,
                 is_elf: bool = None,
                 enable: bool = None):
        super().__init__(filename, category, suffix, is_elf)
        if enable is not None:
            self.enable = enable

    @staticmethod
    def encode(content: Union[str, bytes]) -> str:
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hash_str(content).hexdigest()

    @classmethod
    def create(cls, content: Union[str, bytes], enable: bool = None):
        return cls(cls.encode(content), enable=enable)

    # TODO: Why develop such a function?
    @classmethod
    def late_init(cls):
        output = cls('.no-init')
        output.no_init = True
        return output

    @property
    def path_str(self) -> str:
        return 'cache/' + super().path_str

    def __call__(self, func: Callable):
        # TODO: Now all the functions like func(text, cache) use this.
        #       Maybe it can be prettified?
        def wrapper(*args, **kwargs):
            if self.no_init:
                self.filename = self.encode(args[0])
            if self.exists and self.enable:
                return self.read()
            output = func(*args, **kwargs)
            if self.enable:
                self.write(output)
            return output

        return wrapper


class AudioFile(CommonFile):
    category: str = 'audio'
    suffix: str = 'wav'
    is_elf: bool = True

    def __init__(self, filename: str):
        super().__init__(filename)

    # TODO: Read & write wave files.


class SilkFile(AudioFile):
    suffix: str = 'slk'

    def to_wav(self) -> AudioFile:
        return AudioFile(self.filename)

    @staticmethod
    def silk_encode(wav_data: bytes) -> bytes:
        return pysilk.encode(wav_data)

    def read_from_wav_file(self, wav_path: Union[str, Path] = None) -> bytes:
        if wav_path is None:
            wav_path = self.to_wav().path_str
        elif isinstance(wav_path, Path):
            wav_path = str(wav_path)
        return pysilk.encode_file(wav_path)

    def write_to_wav(self, data: bytes):
        return self.to_wav().write(pysilk.decode(data, to_wav=True))


# Use silk to save cache
class AudioCache(SilkFile, Cache):

    def __init__(self, filename: str, enable: bool = None):
        super(SilkFile, self).__init__(filename)
        if enable is not None:
            self.enable = enable
